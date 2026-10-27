"""Previsión a 7 días: ¿sale a cuenta llenar hoy o esperar?

Con el último año de precios de tu provincia (la media de todas sus gasolineras) se ajusta:

    cambio en 7 días = a + b·(lo que subió el mercado la última semana publicada)
                         + c·(lo que bajó el mercado la última semana publicada)
                         + d·(lo que se movió el precio de la provincia la última semana)

«El mercado» es el gasóleo o la gasolina al por mayor (Nueva York, de la EIA) para el diésel y
las gasolinas, y el Brent para los gases, que no tienen serie abierta. El surtidor va detrás de
lo que paga la gasolinera por el combustible ya refinado, más que del crudo; las subidas y las
bajadas van aparte porque no pasan igual de rápido (suben como cohetes y bajan como plumas); y el
último término recoge que los precios tienen inercia.

Se eligió así comparando variantes en las 52 provincias, reentrenando cada 15 días durante 150
y midiendo solo en días que no había visto (octubre de 2026). Frente al modelo anterior, con el
Brent y sin separar subidas y bajadas, el acierto pasó del 54 al 57 % en gasolina 95 y del 56 al
60 % en diésel; y cuando avisa de un cambio, acierta la dirección el 88 % y el 78 % de las veces
(antes, el 63 y el 74 %). Juntar el Brent con el producto, o mirar dos semanas atrás, lo empeoraba.
También se probaron lo que el precio se aparta de lo que «tocaría» (el margen) y la inercia
separada en subidas y bajadas: no mejoraban. El día de la semana no cuenta: de un lunes al
siguiente es el mismo día.

Se prueba con los últimos 60 días sin usarlos para aprender, se compara con decir siempre «da
igual», y cada día se apunta lo que se prevé, para comprobar después si acertó de verdad. No
prevé sustos (guerras, impuestos, puentes): es una pista, no una garantía.
"""
from __future__ import annotations

import logging
from datetime import date, timedelta

from . import cache, config, db, i18n, mercado, repo
from .formato import moneda, numero

HORIZONTE = 7
RETRASO_MERCADO = 7     # FRED publica el Brent y los productos con cerca de una semana de retraso
DIAS_MINIMOS = 90
DIAS_DE_PRUEBA = 60
UMBRAL = 0.015        # euros por litro: un cambio menor que esto «da igual»

SEMAFOROS = {"llena": "🟢", "igual": "🟡", "espera": "🔴"}     # para Telegram; los nombres, en i18n («sem.*»)

log = logging.getLogger("pumpcast")


def _mover(fecha: str, dias: int) -> str:
    return (date.fromisoformat(fecha) + timedelta(days=dias)).isoformat()


def _conocido(serie: dict[str, float], fecha: str, hoy: str) -> float | None:
    """El valor de mercado de esa fecha tal como se conocía el día `hoy`: nunca mira al futuro."""
    fecha = min(fecha, _mover(hoy, -1))       # el de hoy aún no ha cerrado
    for _ in range(10):
        if fecha in serie:
            return serie[fecha]
        fecha = _mover(fecha, -1)
    return None


def _minimos_cuadrados(filas: list[list[float]], ys: list[float]) -> list[float]:
    """Coeficientes de y = X·c, resolviendo las ecuaciones normales a mano (son 4x4).
    Un pelín de regularización evita que una columna casi vacía lo rompa todo."""
    k = len(filas[0])
    m = [[sum(f[i] * f[j] for f in filas) + (1e-6 if i == j and i else 0.0) for j in range(k)]
         + [sum(f[i] * y for f, y in zip(filas, ys))] for i in range(k)]
    for col in range(k):
        pivote = max(range(col, k), key=lambda r: abs(m[r][col]))
        m[col], m[pivote] = m[pivote], m[col]
        if abs(m[col][col]) < 1e-12:
            return [0.0] * k
        for r in range(k):
            if r != col:
                factor = m[r][col] / m[col][col]
                m[r] = [a - factor * b for a, b in zip(m[r], m[col])]
    return [m[i][k] / m[i][i] for i in range(k)]


def _entradas(fecha: str, precios: dict, referencia: dict) -> list[float] | None:
    """Lo que se sabe el día `fecha`: cuánto subió o bajó el mercado en la última semana publicada
    y cuánto se movió el precio la última semana. Se aprende y se prevé con el mismo retraso, el
    que hay de verdad."""
    antes = _mover(fecha, -HORIZONTE)
    publicado = _mover(fecha, -RETRASO_MERCADO)
    ahora = _conocido(referencia, publicado, fecha)
    semana_antes = _conocido(referencia, _mover(publicado, -HORIZONTE), fecha)
    if antes not in precios or ahora is None or semana_antes is None:
        return None
    movido = ahora - semana_antes
    return [1.0, max(movido, 0.0), min(movido, 0.0), precios[fecha] - precios[antes]]


def ajustar(precios: dict[str, float], referencia: dict[str, float], hasta: str | None = None) -> list[float] | None:
    """Los coeficientes, aprendidos solo con lo que ya se sabía el día `hasta`."""
    filas, cambios = [], []
    for f in sorted(precios):
        despues = _mover(f, HORIZONTE)
        if despues not in precios or (hasta and despues > hasta):
            continue
        x = _entradas(f, precios, referencia)
        if x:
            filas.append(x)
            cambios.append(precios[despues] - precios[f])
    if len(cambios) < DIAS_MINIMOS - 2 * HORIZONTE:
        return None
    return _minimos_cuadrados(filas, cambios)


def _prever(fecha: str, precios: dict, referencia: dict, coef: list[float]) -> float | None:
    x = _entradas(fecha, precios, referencia)
    return sum(c * v for c, v in zip(coef, x)) if x else None


def semaforo(cambio: float) -> str:
    if cambio >= UMBRAL:
        return "llena"
    if cambio <= -UMBRAL:
        return "espera"
    return "igual"


def acierta(previsto: str, real: float) -> bool:
    """Si hacer caso habría salido bien: subió cuando dijo llena, bajó cuando dijo espera,
    o se movió poco cuando dijo que daba igual."""
    if previsto == "llena":
        return real > 0
    if previsto == "espera":
        return real < 0
    return abs(real) < 2 * UMBRAL


def _datos(provincia: str, comb: str) -> dict:
    return {f["fecha"]: f["media"] for f in repo.serie_provincia(provincia, comb, dias=400)}


def _prueba(precios: dict, referencia: dict) -> dict | None:
    """Cuánto habría acertado en los últimos 60 días, y cuánto decir siempre «da igual»."""
    fechas = sorted(precios)
    corte = _mover(fechas[-1], -DIAS_DE_PRUEBA)
    coef = ajustar(precios, referencia, hasta=corte)
    if not coef:
        return None
    aciertos = total = siempre_igual = 0
    errores = []
    for f in fechas:
        despues = _mover(f, HORIZONTE)
        if f <= corte or despues not in precios:
            continue
        cambio = _prever(f, precios, referencia, coef)
        if cambio is None:
            continue
        real = precios[despues] - precios[f]
        total += 1
        aciertos += acierta(semaforo(cambio), real)
        siempre_igual += acierta("igual", real)
        errores.append(abs(cambio - real))
    if not total:
        return None
    return {"aciertos": aciertos, "total": total, "error_medio": sum(errores) / total,
            "siempre_igual": siempre_igual}


def _seguimiento(provincia: str, comb: str, precios: dict) -> dict:
    with db.sesion() as con:
        filas = con.execute("SELECT fecha, semaforo FROM previsiones WHERE provincia = ? AND combustible = ?",
                            (provincia, comb)).fetchall()
    aciertos = total = 0
    for f in filas:
        despues = _mover(f["fecha"], HORIZONTE)
        if f["fecha"] in precios and despues in precios:
            total += 1
            aciertos += acierta(f["semaforo"], precios[despues] - precios[f["fecha"]])
    return {"aciertos": aciertos, "total": total, "apuntadas": len(filas)}


def prevision(provincia: str | None, comb: str, litros: float = 40, series: dict | None = None) -> dict:
    """La previsión de una provincia. `series` (las de mercado.series()) se puede pasar para no
    leerlas en cada una. Es igual para todos hasta que llegan datos nuevos: se guarda en memoria
    (ver cache.py)."""
    p = dict(cache.recordar(("prevision", provincia, comb), lambda: _prevision(provincia, comb, series)))
    if p.get("lista"):
        p["euros_deposito"] = abs(p["cambio"]) * float(litros)
    return p


def _referencia(comb: str, series: dict) -> tuple[str, dict]:
    """El mercado que sigue ese combustible; el Brent si no hay serie del producto."""
    nombre = mercado.REFERENCIA.get(comb, "brent")
    if not series.get(nombre):
        nombre = "brent"
    return nombre, series.get(nombre) or {}


def _semana(serie: dict, hoy: str) -> tuple[float | None, float | None]:
    """El último valor publicado y cuánto ha cambiado (en tanto por uno) en la semana que acaba en
    él, no en la que acaba hoy: los últimos días aún no están publicados."""
    ultimo = max((f for f in serie if f < hoy), default=None)
    if ultimo is None:
        return None, None
    ahora, antes = serie[ultimo], _conocido(serie, _mover(ultimo, -HORIZONTE), hoy)
    return ahora, (ahora / antes - 1) if antes else None


def _prevision(provincia: str | None, comb: str, series: dict | None = None) -> dict:
    if not provincia:
        return {"lista": False, "dias": 0, "faltan": DIAS_MINIMOS + HORIZONTE}
    precios = _datos(provincia, comb)
    series = mercado.series() if series is None else series
    nombre, referencia = _referencia(comb, series)
    if len(precios) < DIAS_MINIMOS + HORIZONTE or not referencia:
        return {"lista": False, "dias": len(precios), "faltan": max(0, DIAS_MINIMOS + HORIZONTE - len(precios))}
    coef = ajustar(precios, referencia)
    hoy = max(precios)
    cambio = _prever(hoy, precios, referencia, coef) if coef else None
    if cambio is None:
        return {"lista": False, "dias": len(precios), "faltan": 0}
    clave = semaforo(cambio)
    brent = series.get("brent") or {}
    brent_hoy, brent_semana = _semana(brent, hoy)
    return {
        "lista": True,
        "provincia": provincia,
        "nombre_provincia": config.NOMBRE_PROVINCIA.get(provincia, provincia),
        "fecha": hoy,
        "cambio": cambio,
        "semaforo": clave,
        "icono": SEMAFOROS[clave],
        "brent": brent_hoy,
        "brent_fecha": max((f for f in brent if f < hoy), default=None),
        "brent_semana": brent_semana,
        "mercado": nombre,                                  # "gasoil", "gasolina" o "brent"
        "mercado_semana": _semana(referencia, hoy)[1],
        "prueba": _prueba(precios, referencia),
        "precio_semana": precios[hoy] - precios[_mover(hoy, -HORIZONTE)] if _mover(hoy, -HORIZONTE) in precios else None,
        "prueba": _prueba(precios, referencia),
        "seguimiento": _seguimiento(provincia, comb, precios),
    }


def titulo(p: dict, lang: str) -> str:
    return i18n.t(lang, "sem." + p["semaforo"])


def frase(p: dict, lang: str) -> str:
    """La previsión en una frase, para la web y para Telegram."""
    return i18n.t(lang, "frase." + p["semaforo"], cts=numero(abs(p["cambio"]) * 100, 1, lang),
                  euros=moneda(p["euros_deposito"], 2, lang))


_probadas: set[tuple[str, str, str]] = set()     # (fecha, provincia, combustible) sin datos suficientes


def apuntar_de_hoy() -> int:
    """Guarda la previsión del día de cada provincia y combustible (una vez por día de datos),
    para poder decir luego cuántas acertó. Devuelve cuántas ha apuntado."""
    with db.sesion() as con:
        pendientes = con.execute(
            """SELECT m.provincia, m.combustible, m.fecha FROM medias_provincia m
               JOIN (SELECT combustible, MAX(fecha) AS fecha FROM precios GROUP BY combustible) u
                 ON u.combustible = m.combustible AND u.fecha = m.fecha
               WHERE NOT EXISTS (SELECT 1 FROM previsiones p WHERE p.provincia = m.provincia
                                 AND p.combustible = m.combustible AND p.fecha = m.fecha)""").fetchall()
    pendientes = [f for f in pendientes if (f["fecha"], f["provincia"], f["combustible"]) not in _probadas]
    if not pendientes:
        return 0
    series = mercado.series()
    apuntadas = []
    for f in pendientes:
        p = prevision(f["provincia"], f["combustible"], series=series)
        if p["lista"] and p["fecha"] == f["fecha"]:
            apuntadas.append((f["fecha"], f["provincia"], f["combustible"], p["cambio"], p["semaforo"]))
        else:
            _probadas.add((f["fecha"], f["provincia"], f["combustible"]))
    with db.sesion() as con:
        con.executemany("INSERT OR IGNORE INTO previsiones (fecha, provincia, combustible, cambio, semaforo) "
                        "VALUES (?, ?, ?, ?, ?)", apuntadas)
    if apuntadas:
        log.info("Previsiones apuntadas: %d", len(apuntadas))
    return len(apuntadas)

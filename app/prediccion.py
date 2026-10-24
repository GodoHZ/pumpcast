"""Previsión a 7 días: ¿sale a cuenta llenar hoy o esperar?

Con el último año de precios de tu zona se ajusta:

    cambio en 7 días = a + b·(lo que se movió el Brent en euros la última semana)
                         + c·(lo que se movió el precio de tu zona la última semana)

El primer término recoge que el surtidor va detrás del petróleo; el segundo, que los
precios tienen inercia (suben como cohetes y bajan como plumas). Se probó también buscar
el retraso exacto respecto al Brent y lo que el precio se aparta de lo que «tocaría»: con
datos reales no acertaba más que decir «no va a cambiar», y esto sí.

Se prueba con los últimos 60 días sin usarlos para aprender, y cada día se apunta lo que
se prevé, para comprobar después si acertó de verdad. No prevé sustos (guerras,
impuestos, puentes): es una pista, no una garantía.
"""
from __future__ import annotations

from datetime import date, timedelta

from . import db, i18n, mercado, repo
from .formato import moneda, numero

HORIZONTE = 7
DIAS_MINIMOS = 90
DIAS_DE_PRUEBA = 60
UMBRAL = 0.015        # euros por litro: un cambio menor que esto «da igual»

SEMAFOROS = {"llena": "🟢", "igual": "🟡", "espera": "🔴"}     # los nombres, en i18n («sem.*»)


def _mover(fecha: str, dias: int) -> str:
    return (date.fromisoformat(fecha) + timedelta(days=dias)).isoformat()


def _brent(brent: dict[str, float], fecha: str, hoy: str) -> float | None:
    """El Brent de esa fecha tal como se conocía el día `hoy`: nunca mira al futuro."""
    fecha = min(fecha, _mover(hoy, -1))       # el de hoy aún no ha cerrado
    for _ in range(7):
        if fecha in brent:
            return brent[fecha]
        fecha = _mover(fecha, -1)
    return None


def _minimos_cuadrados(filas: list[list[float]], ys: list[float]) -> list[float]:
    """Coeficientes de y = X·c, resolviendo las ecuaciones normales a mano (son 3x3).
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


def _entradas(fecha: str, precios: dict, brent: dict) -> list[float] | None:
    """Lo que se sabe el día `fecha`: cuánto se movió el Brent y el precio la última semana."""
    antes = _mover(fecha, -HORIZONTE)
    brent_ahora = _brent(brent, fecha, fecha)
    brent_antes = _brent(brent, _mover(fecha, -HORIZONTE), fecha)
    if antes not in precios or brent_ahora is None or brent_antes is None:
        return None
    return [1.0, brent_ahora - brent_antes, precios[fecha] - precios[antes]]


def ajustar(precios: dict[str, float], brent: dict[str, float], hasta: str | None = None) -> list[float] | None:
    """Los coeficientes, aprendidos solo con lo que ya se sabía el día `hasta`."""
    filas, cambios = [], []
    for f in sorted(precios):
        despues = _mover(f, HORIZONTE)
        if despues not in precios or (hasta and despues > hasta):
            continue
        x = _entradas(f, precios, brent)
        if x:
            filas.append(x)
            cambios.append(precios[despues] - precios[f])
    if len(cambios) < DIAS_MINIMOS - 2 * HORIZONTE:
        return None
    return _minimos_cuadrados(filas, cambios)


def _prever(fecha: str, precios: dict, brent: dict, coef: list[float]) -> float | None:
    x = _entradas(fecha, precios, brent)
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


def _datos(aj: dict, comb: str) -> tuple[dict, dict]:
    precios = {f["fecha"]: f["media"] for f in repo.serie_zona(aj, comb, dias=400)}
    return precios, mercado.brent_euros()


def _prueba(precios: dict, brent: dict) -> dict | None:
    fechas = sorted(precios)
    corte = _mover(fechas[-1], -DIAS_DE_PRUEBA)
    coef = ajustar(precios, brent, hasta=corte)
    if not coef:
        return None
    aciertos = total = 0
    errores = []
    for f in fechas:
        despues = _mover(f, HORIZONTE)
        if f <= corte or despues not in precios:
            continue
        cambio = _prever(f, precios, brent, coef)
        if cambio is None:
            continue
        real = precios[despues] - precios[f]
        total += 1
        aciertos += acierta(semaforo(cambio), real)
        errores.append(abs(cambio - real))
    if not total:
        return None
    return {"aciertos": aciertos, "total": total, "error_medio": sum(errores) / total}


def _seguimiento(comb: str, precios: dict) -> dict:
    with db.sesion() as con:
        filas = con.execute("SELECT fecha, semaforo FROM predicciones WHERE combustible = ?", (comb,)).fetchall()
    aciertos = total = 0
    for f in filas:
        despues = _mover(f["fecha"], HORIZONTE)
        if f["fecha"] in precios and despues in precios:
            total += 1
            aciertos += acierta(f["semaforo"], precios[despues] - precios[f["fecha"]])
    return {"aciertos": aciertos, "total": total, "apuntadas": len(filas)}


def prevision(aj: dict, comb: str) -> dict:
    precios, brent = _datos(aj, comb)
    if len(precios) < DIAS_MINIMOS + HORIZONTE or not brent:
        return {"lista": False, "dias": len(precios), "faltan": max(0, DIAS_MINIMOS + HORIZONTE - len(precios))}
    coef = ajustar(precios, brent)
    hoy = max(precios)
    cambio = _prever(hoy, precios, brent, coef) if coef else None
    if cambio is None:
        return {"lista": False, "dias": len(precios), "faltan": 0}
    clave = semaforo(cambio)
    brent_hoy = _brent(brent, hoy, hoy)
    brent_antes = _brent(brent, _mover(hoy, -HORIZONTE), hoy)
    return {
        "lista": True,
        "fecha": hoy,
        "cambio": cambio,
        "semaforo": clave,
        "icono": SEMAFOROS[clave],
        "euros_deposito": abs(cambio) * float(aj["litros"]),
        "brent": brent_hoy,
        "brent_semana": (brent_hoy / brent_antes - 1) if brent_hoy and brent_antes else None,
        "precio_semana": precios[hoy] - precios[_mover(hoy, -HORIZONTE)] if _mover(hoy, -HORIZONTE) in precios else None,
        "prueba": _prueba(precios, brent),
        "seguimiento": _seguimiento(comb, precios),
    }


def titulo(p: dict, lang: str) -> str:
    return i18n.t(lang, "sem." + p["semaforo"])


def frase(p: dict, lang: str) -> str:
    """La previsión en una frase, para la web y para Telegram."""
    return i18n.t(lang, "frase." + p["semaforo"], cts=numero(abs(p["cambio"]) * 100, 1, lang),
                  euros=moneda(p["euros_deposito"], 2, lang))


def apuntar_de_hoy(aj: dict) -> None:
    """Guarda la previsión del día para el combustible de Ajustes (una vez por día de datos)."""
    comb = aj["combustible"]
    with db.sesion() as con:
        hoy = con.execute("SELECT MAX(fecha) FROM precios WHERE combustible = ?", (comb,)).fetchone()[0]
        if not hoy or con.execute("SELECT 1 FROM predicciones WHERE fecha = ? AND combustible = ?",
                                  (hoy, comb)).fetchone():
            return
    p = prevision(aj, comb)
    if p["lista"] and p["fecha"] == hoy:
        with db.sesion() as con:
            con.execute("INSERT OR IGNORE INTO predicciones (fecha, combustible, cambio, semaforo) "
                        "VALUES (?, ?, ?, ?)", (hoy, comb, p["cambio"], p["semaforo"]))

"""Lecturas y consultas sobre la base de datos.

"Hoy" es siempre el último día con datos de ese combustible, no la fecha del reloj: así,
si el Ministerio se retrasa o la app estuvo parada, se sigue viendo lo último que hay.

Hay unas 11.000 gasolineras: las consultas por radio buscan primero en un recuadro
alrededor del punto (con el índice por latitud) y luego miden la distancia de verdad.
"""
from __future__ import annotations

from collections import defaultdict
from datetime import date, datetime, timedelta
from math import asin, cos, radians, sin, sqrt

from . import cache, config, db


def ahora_iso() -> str:
    return datetime.now(config.TZ).isoformat(timespec="seconds")


def distancia_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    dlat, dlon = radians(lat2 - lat1), radians(lon2 - lon1)
    a = sin(dlat / 2) ** 2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlon / 2) ** 2
    return 2 * 6371 * asin(sqrt(a))


# --- Lecturas del Ministerio -------------------------------------------------------------

_INSERTAR_ESTACION = """
    INSERT {o} INTO estaciones (id, rotulo, direccion, localidad, municipio, provincia, provincia_id,
                                cp, lat, lon, horario, vista)
    VALUES (:id, :rotulo, :direccion, :localidad, :municipio, :provincia, :provincia_id,
            :cp, :lat, :lon, :horario, :vista)"""

_MEDIAS_DEL_DIA = """
    INSERT INTO medias_provincia (fecha, provincia, combustible, media, minimo, estaciones)
    SELECT p.fecha, e.provincia_id, p.combustible, AVG(p.precio), MIN(p.precio), COUNT(*)
    FROM precios p JOIN estaciones e ON e.id = p.estacion_id
    WHERE p.fecha = ? AND e.provincia_id IS NOT NULL
    GROUP BY e.provincia_id, p.combustible
    ON CONFLICT(provincia, combustible, fecha) DO UPDATE SET
        media = excluded.media, minimo = excluded.minimo, estaciones = excluded.estaciones"""


def guardar_lectura(momento: datetime, estaciones: list[dict]) -> None:
    fecha = momento.date().isoformat()
    vista = ahora_iso()
    with db.sesion() as con:
        con.executemany(
            _INSERTAR_ESTACION.format(o="") + """
               ON CONFLICT(id) DO UPDATE SET
                   rotulo = excluded.rotulo, direccion = excluded.direccion,
                   localidad = excluded.localidad, municipio = excluded.municipio,
                   provincia = excluded.provincia, provincia_id = excluded.provincia_id,
                   cp = excluded.cp, lat = excluded.lat, lon = excluded.lon,
                   horario = excluded.horario, vista = excluded.vista""",
            [{**e, "vista": vista} for e in estaciones])
        con.executemany(
            """INSERT INTO precios (estacion_id, combustible, fecha, precio) VALUES (?, ?, ?, ?)
               ON CONFLICT(estacion_id, combustible, fecha) DO UPDATE SET precio = excluded.precio""",
            [(e["id"], comb, fecha, precio) for e in estaciones for comb, precio in e["precios"].items()])
        con.execute(_MEDIAS_DEL_DIA, (fecha,))
        con.execute("INSERT INTO lecturas (momento, fecha_datos, estaciones) VALUES (?, ?, ?)",
                    (vista, momento.isoformat(sep=" "), len(estaciones)))
    cache.invalidar()


def _medias(estaciones: list[dict]) -> dict[tuple[str, str], list[float]]:
    grupos: dict[tuple[str, str], list[float]] = defaultdict(list)
    for e in estaciones:
        if e.get("provincia_id"):
            for comb, precio in e["precios"].items():
                grupos[(e["provincia_id"], comb)].append(precio)
    return grupos


def guardar_historico(momento: datetime, estaciones: list[dict], con_precios: bool = True) -> None:
    """Un día pasado del histórico del Ministerio. Siempre guarda las medias por provincia;
    los precios de cada gasolinera, solo si `con_precios` (los días recientes). No pisa lo
    que ya hubiera de ese día ni cuenta como lectura (las lecturas marcan cuándo toca la
    siguiente)."""
    fecha = momento.date().isoformat()
    with db.sesion() as con:
        if con_precios:
            con.executemany(_INSERTAR_ESTACION.format(o="OR IGNORE"), [{**e, "vista": fecha} for e in estaciones])
            con.executemany(
                "INSERT OR IGNORE INTO precios (estacion_id, combustible, fecha, precio) VALUES (?, ?, ?, ?)",
                [(e["id"], comb, fecha, precio) for e in estaciones for comb, precio in e["precios"].items()])
        con.executemany(
            "INSERT OR IGNORE INTO medias_provincia (fecha, provincia, combustible, media, minimo, estaciones) "
            "VALUES (?, ?, ?, ?, ?, ?)",
            [(fecha, prov, comb, sum(v) / len(v), min(v), len(v)) for (prov, comb), v in _medias(estaciones).items()])
        con.execute("INSERT OR IGNORE INTO historico (fecha, provincia) VALUES (?, 'ES')", (fecha,))
    cache.invalidar()


def dias_sin_historico(dias: int, hoy: date) -> list[date]:
    """Días de los últimos `dias` que faltan, del más reciente al más antiguo."""
    with db.sesion() as con:
        hechos = {f[0] for f in con.execute("SELECT fecha FROM historico WHERE provincia = 'ES'")}
    candidatos = (hoy - timedelta(days=n) for n in range(1, dias + 1))
    return [d for d in candidatos if d.isoformat() not in hechos]


def borrar_precios_viejos(hoy: date) -> int:
    """Los precios de cada gasolinera de hace más de DIAS_CON_PRECIOS días (las medias se quedan)."""
    with db.sesion() as con:
        borrados = con.execute("DELETE FROM precios WHERE fecha < ?",
                               ((hoy - timedelta(days=config.DIAS_CON_PRECIOS)).isoformat(),)).rowcount
    cache.invalidar()
    return borrados


def apuntar_error(texto: str) -> None:
    with db.sesion() as con:
        con.execute("INSERT INTO lecturas (momento, error) VALUES (?, ?)", (ahora_iso(), texto))


def ultima_lectura(con_errores: bool = False):
    filtro = "" if con_errores else " WHERE error IS NULL"
    with db.sesion() as con:
        return con.execute(f"SELECT * FROM lecturas{filtro} ORDER BY momento DESC LIMIT 1").fetchone()


# --- Ajustes del panel de administración y secretos --------------------------------------

def ajustes() -> dict:
    valores = dict(config.AJUSTES_POR_DEFECTO)
    with db.sesion() as con:
        for fila in con.execute("SELECT clave, valor FROM ajustes"):
            if fila["clave"] in valores:
                valores[fila["clave"]] = fila["valor"]
    return valores


def guardar_ajustes(valores: dict) -> None:
    with db.sesion() as con:
        con.executemany(
            "INSERT INTO ajustes (clave, valor) VALUES (?, ?) "
            "ON CONFLICT(clave) DO UPDATE SET valor = excluded.valor",
            [(k, str(v)) for k, v in valores.items() if k in config.AJUSTES_POR_DEFECTO])


def secreto(clave: str) -> str | None:
    with db.sesion() as con:
        fila = con.execute("SELECT valor FROM secretos WHERE clave = ?", (clave,)).fetchone()
    return fila[0] if fila else None


def guardar_secreto(clave: str, valor: str | None) -> None:
    with db.sesion() as con:
        if valor is None:
            con.execute("DELETE FROM secretos WHERE clave = ?", (clave,))
        else:
            con.execute("INSERT INTO secretos (clave, valor) VALUES (?, ?) "
                        "ON CONFLICT(clave) DO UPDATE SET valor = excluded.valor", (clave, valor))


# --- Consultas ---------------------------------------------------------------------------

def _casa(aj: dict) -> tuple[float, float, float]:
    return float(aj["lat"]), float(aj["lon"]), float(aj["radio_km"])


def _dia_referencia(con, comb: str) -> str | None:
    return con.execute("SELECT MAX(fecha) FROM precios WHERE combustible = ?", (comb,)).fetchone()[0]


def _hace(dia: str, dias: int) -> str:
    return (date.fromisoformat(dia) - timedelta(days=dias)).isoformat()


def _alrededor(con, lat: float, lon: float, radio: float) -> list[tuple[dict, float]]:
    """Las gasolineras a menos de `radio` km, con su distancia."""
    dlat = radio / 111.0
    dlon = radio / (111.0 * max(cos(radians(lat)), 0.01))
    filas = con.execute("SELECT * FROM estaciones WHERE lat BETWEEN ? AND ? AND lon BETWEEN ? AND ?",
                        (lat - dlat, lat + dlat, lon - dlon, lon + dlon)).fetchall()
    cerca = []
    for f in filas:
        distancia = distancia_km(lat, lon, f["lat"], f["lon"])
        if distancia <= radio:
            cerca.append((dict(f), distancia))
    return cerca


def cercanas(aj: dict, comb: str, radio_km: float | None = None) -> list[dict]:
    """Estaciones con precio de hoy dentro del radio, de la más barata a la más cara."""
    lat, lon, radio = _casa(aj)
    clave = ("cercanas", round(lat, 4), round(lon, 4), radio if radio_km is None else radio_km, comb)
    return [dict(e) for e in cache.recordar(clave, lambda: _cercanas(aj, comb, radio_km))]   # copias: se les añade cosas


def _cercanas(aj: dict, comb: str, radio_km: float | None = None) -> list[dict]:
    lat, lon, radio = _casa(aj)
    if radio_km is not None:
        radio = radio_km
    with db.sesion() as con:
        hoy = _dia_referencia(con, comb)
        if not hoy:
            return []
        cerca = {e["id"]: (e, d) for e, d in _alrededor(con, lat, lon, radio)}
        if not cerca:
            return []
        marcas = ",".join("?" * len(cerca))
        filas = con.execute(
            f"SELECT estacion_id, precio FROM precios WHERE combustible = ? AND fecha = ? "
            f"AND estacion_id IN ({marcas})", (comb, hoy, *cerca)).fetchall()
    lista = [{**cerca[f[0]][0], "precio": f[1], "distancia": cerca[f[0]][1]} for f in filas]
    lista.sort(key=lambda e: (e["precio"], e["distancia"]))
    return lista


def serie_zona(aj: dict, comb: str, dias: int = 90) -> list[dict]:
    """Media y mínimo de cada día entre las estaciones del radio."""
    lat, lon, radio = _casa(aj)
    clave = ("serie", round(lat, 4), round(lon, 4), radio, comb, dias)
    return [dict(f) for f in cache.recordar(clave, lambda: _serie_zona(aj, comb, dias))]


def _serie_zona(aj: dict, comb: str, dias: int = 90) -> list[dict]:
    lat, lon, radio = _casa(aj)
    with db.sesion() as con:
        hoy = _dia_referencia(con, comb)
        if not hoy:
            return []
        ids = [e["id"] for e, _ in _alrededor(con, lat, lon, radio)]
        if not ids:
            return []
        marcas = ",".join("?" * len(ids))
        # El «+» impide usar el índice por combustible y fecha: con él, SQLite recorre los precios de
        # toda España (unas 900.000 filas, 400 ms); por gasolinera son unas pocas miles (30 ms).
        filas = con.execute(
            f"SELECT fecha, AVG(precio) AS media, MIN(precio) AS minimo, COUNT(*) AS estaciones "
            f"FROM precios WHERE +combustible = ? AND fecha > ? AND estacion_id IN ({marcas}) "
            f"GROUP BY fecha ORDER BY fecha", (comb, _hace(hoy, dias), *ids)).fetchall()
    return [dict(f) for f in filas]


def provincia_de(lat: float, lon: float) -> str | None:
    """La provincia de la gasolinera más cercana: la que se usa para la previsión."""
    return cache.recordar(("provincia", round(lat, 3), round(lon, 3)), lambda: _provincia_de(lat, lon))


def _provincia_de(lat: float, lon: float) -> str | None:
    with db.sesion() as con:
        for radio in (15, 60):
            cerca = [(d, e["provincia_id"]) for e, d in _alrededor(con, lat, lon, radio) if e["provincia_id"]]
            if cerca:
                return min(cerca)[1]
    return None


def serie_provincia(provincia: str, comb: str, dias: int = 400) -> list[dict]:
    with db.sesion() as con:
        hoy = con.execute("SELECT MAX(fecha) FROM medias_provincia WHERE provincia = ? AND combustible = ?",
                          (provincia, comb)).fetchone()[0]
        if not hoy:
            return []
        filas = con.execute(
            "SELECT fecha, media, minimo FROM medias_provincia WHERE provincia = ? AND combustible = ? "
            "AND fecha > ? ORDER BY fecha", (provincia, comb, _hace(hoy, dias))).fetchall()
    return [dict(f) for f in filas]


def por_dia_semana(serie: list[dict]) -> list[dict]:
    """Media de cada día de la semana (0 = lunes)."""
    grupos: dict[int, list[float]] = {i: [] for i in range(7)}
    for f in serie:
        grupos[date.fromisoformat(f["fecha"]).weekday()].append(f["media"])
    return [{"dia": i, "media": sum(v) / len(v) if v else None, "dias": len(v)} for i, v in grupos.items()]


def estacion(estacion_id: int) -> dict | None:
    with db.sesion() as con:
        fila = con.execute("SELECT * FROM estaciones WHERE id = ?", (estacion_id,)).fetchone()
    return dict(fila) if fila else None


def favoritas(aj: dict, comb: str, ids: list[int]) -> list[dict]:
    """Las favoritas del visitante con su precio de hoy, estén donde estén."""
    if not ids:
        return []
    lat, lon, _ = _casa(aj)
    marcas = ",".join("?" * len(ids))
    with db.sesion() as con:
        hoy = _dia_referencia(con, comb)
        filas = con.execute(
            f"SELECT e.*, p.precio FROM estaciones e LEFT JOIN precios p ON p.estacion_id = e.id "
            f"AND p.combustible = ? AND p.fecha = ? WHERE e.id IN ({marcas})", (comb, hoy, *ids)).fetchall()
    lista = [{**dict(f), "distancia": distancia_km(lat, lon, f["lat"], f["lon"])} for f in filas]
    return sorted(lista, key=lambda e: ids.index(e["id"]))


def precios_actuales(estacion_id: int) -> dict[str, float]:
    """Último precio de cada combustible, solo si es del último día con datos."""
    with db.sesion() as con:
        resultado = {}
        for comb in config.COMBUSTIBLES:
            hoy = _dia_referencia(con, comb)
            fila = hoy and con.execute("SELECT precio FROM precios WHERE estacion_id = ? AND combustible = ? "
                                       "AND fecha = ?", (estacion_id, comb, hoy)).fetchone()
            if fila:
                resultado[comb] = fila[0]
    return resultado


def historial(estacion_id: int, comb: str, dias: int = 90) -> list[dict]:
    with db.sesion() as con:
        hoy = _dia_referencia(con, comb)
        if not hoy:
            return []
        filas = con.execute(
            "SELECT fecha, precio FROM precios WHERE estacion_id = ? AND combustible = ? AND fecha > ? "
            "ORDER BY fecha", (estacion_id, comb, _hace(hoy, dias))).fetchall()
    return [dict(f) for f in filas]


# --- Avisos ya enviados ------------------------------------------------------------------

def aviso_enviado(clave: str) -> bool:
    with db.sesion() as con:
        return con.execute("SELECT 1 FROM avisos WHERE clave = ?", (clave,)).fetchone() is not None


def marcar_aviso(clave: str) -> None:
    with db.sesion() as con:
        con.execute("INSERT OR IGNORE INTO avisos (clave, momento) VALUES (?, ?)", (clave, ahora_iso()))

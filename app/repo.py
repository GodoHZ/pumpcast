"""Lecturas y consultas sobre la base de datos.

"Hoy" es siempre el último día con datos de ese combustible, no la fecha del reloj: así,
si el Ministerio se retrasa o la app estuvo parada, se sigue viendo lo último que hay.
"""
from __future__ import annotations

from datetime import date, datetime, timedelta
from math import asin, cos, radians, sin, sqrt

from . import config, db


def ahora_iso() -> str:
    return datetime.now(config.TZ).isoformat(timespec="seconds")


def distancia_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    dlat, dlon = radians(lat2 - lat1), radians(lon2 - lon1)
    a = sin(dlat / 2) ** 2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlon / 2) ** 2
    return 2 * 6371 * asin(sqrt(a))


# --- Lecturas del Ministerio -------------------------------------------------------------

def guardar_lectura(momento: datetime, estaciones: list[dict]) -> None:
    fecha = momento.date().isoformat()
    vista = ahora_iso()
    with db.sesion() as con:
        con.executemany(
            """INSERT INTO estaciones (id, rotulo, direccion, localidad, municipio, provincia, cp,
                                       lat, lon, horario, vista)
               VALUES (:id, :rotulo, :direccion, :localidad, :municipio, :provincia, :cp,
                       :lat, :lon, :horario, :vista)
               ON CONFLICT(id) DO UPDATE SET
                   rotulo = excluded.rotulo, direccion = excluded.direccion,
                   localidad = excluded.localidad, municipio = excluded.municipio,
                   provincia = excluded.provincia, cp = excluded.cp, lat = excluded.lat,
                   lon = excluded.lon, horario = excluded.horario, vista = excluded.vista""",
            [{**e, "vista": vista} for e in estaciones])
        con.executemany(
            """INSERT INTO precios (estacion_id, combustible, fecha, precio) VALUES (?, ?, ?, ?)
               ON CONFLICT(estacion_id, combustible, fecha) DO UPDATE SET precio = excluded.precio""",
            [(e["id"], comb, fecha, precio) for e in estaciones for comb, precio in e["precios"].items()])
        con.execute("INSERT INTO lecturas (momento, fecha_datos, estaciones) VALUES (?, ?, ?)",
                    (vista, momento.isoformat(sep=" "), len(estaciones)))


def guardar_historico(momento: datetime, estaciones: list[dict], provincia: str) -> None:
    """Un día pasado del histórico del Ministerio. No toca los datos actuales de las
    estaciones ni cuenta como lectura (las lecturas marcan cuándo toca la siguiente)."""
    fecha = momento.date().isoformat()
    with db.sesion() as con:
        con.executemany(
            """INSERT OR IGNORE INTO estaciones (id, rotulo, direccion, localidad, municipio, provincia,
                                                 cp, lat, lon, horario, vista)
               VALUES (:id, :rotulo, :direccion, :localidad, :municipio, :provincia, :cp,
                       :lat, :lon, :horario, :vista)""",
            [{**e, "vista": fecha} for e in estaciones])
        con.executemany(
            "INSERT OR IGNORE INTO precios (estacion_id, combustible, fecha, precio) VALUES (?, ?, ?, ?)",
            [(e["id"], comb, fecha, precio) for e in estaciones for comb, precio in e["precios"].items()])
        con.execute("INSERT OR IGNORE INTO historico (fecha, provincia) VALUES (?, ?)", (fecha, provincia))


def dias_sin_historico(provincia: str, dias: int, hoy: date) -> list[date]:
    """Días de los últimos `dias` que faltan, del más reciente al más antiguo."""
    with db.sesion() as con:
        hechos = {f[0] for f in con.execute("SELECT fecha FROM historico WHERE provincia = ?", (provincia,))}
        con_lectura = {f[0][:10] for f in con.execute(
            "SELECT fecha_datos FROM lecturas WHERE fecha_datos IS NOT NULL")}
    candidatos = (hoy - timedelta(days=n) for n in range(1, dias + 1))
    return [d for d in candidatos if d.isoformat() not in hechos and d.isoformat() not in con_lectura]


def apuntar_error(texto: str) -> None:
    with db.sesion() as con:
        con.execute("INSERT INTO lecturas (momento, error) VALUES (?, ?)", (ahora_iso(), texto))


def ultima_lectura(con_errores: bool = False):
    filtro = "" if con_errores else " WHERE error IS NULL"
    with db.sesion() as con:
        return con.execute(f"SELECT * FROM lecturas{filtro} ORDER BY momento DESC LIMIT 1").fetchone()


# --- Ajustes -----------------------------------------------------------------------------

def ajustes() -> dict:
    valores = dict(config.AJUSTES_POR_DEFECTO)
    with db.sesion() as con:
        for fila in con.execute("SELECT clave, valor FROM ajustes"):
            if fila["clave"] in valores:
                valores[fila["clave"]] = fila["valor"]
    return valores


def provincias(aj: dict) -> list[str]:
    return [p for p in aj["provincias"].split(",") if p in config.CODIGOS_PROVINCIA]


def guardar_ajustes(valores: dict) -> None:
    with db.sesion() as con:
        con.executemany(
            "INSERT INTO ajustes (clave, valor) VALUES (?, ?) "
            "ON CONFLICT(clave) DO UPDATE SET valor = excluded.valor",
            [(k, str(v)) for k, v in valores.items() if k in config.AJUSTES_POR_DEFECTO])


# --- Consultas ---------------------------------------------------------------------------

def _casa(aj: dict) -> tuple[float, float, float]:
    return float(aj["lat"]), float(aj["lon"]), float(aj["radio_km"])


def _dia_referencia(con, comb: str) -> str | None:
    return con.execute("SELECT MAX(fecha) FROM precios WHERE combustible = ?", (comb,)).fetchone()[0]


def _hace(dia: str, dias: int) -> str:
    return (date.fromisoformat(dia) - timedelta(days=dias)).isoformat()


def cercanas(aj: dict, comb: str, radio_km: float | None = None) -> list[dict]:
    """Estaciones con precio de hoy dentro del radio, de la más barata a la más cara."""
    lat, lon, radio = _casa(aj)
    if radio_km is not None:
        radio = radio_km
    with db.sesion() as con:
        hoy = _dia_referencia(con, comb)
        if not hoy:
            return []
        medias = {f[0]: f[1] for f in con.execute(
            "SELECT estacion_id, AVG(precio) FROM precios WHERE combustible = ? AND fecha >= ? "
            "GROUP BY estacion_id", (comb, _hace(hoy, 30)))}
        filas = con.execute(
            "SELECT e.*, p.precio FROM precios p JOIN estaciones e ON e.id = p.estacion_id "
            "WHERE p.combustible = ? AND p.fecha = ?", (comb, hoy)).fetchall()
    lista = []
    for f in filas:
        distancia = distancia_km(lat, lon, f["lat"], f["lon"])
        if distancia <= radio:
            lista.append({**dict(f), "distancia": distancia, "media_30": medias.get(f["id"])})
    lista.sort(key=lambda e: (e["precio"], e["distancia"]))
    return lista


def serie_zona(aj: dict, comb: str, dias: int = 90) -> list[dict]:
    """Media y mínimo de cada día entre las estaciones del radio."""
    lat, lon, radio = _casa(aj)
    with db.sesion() as con:
        hoy = _dia_referencia(con, comb)
        if not hoy:
            return []
        ids = [f["id"] for f in con.execute("SELECT id, lat, lon FROM estaciones")
               if distancia_km(lat, lon, f["lat"], f["lon"]) <= radio]
        if not ids:
            return []
        marcas = ",".join("?" * len(ids))
        filas = con.execute(
            f"SELECT fecha, AVG(precio) AS media, MIN(precio) AS minimo, COUNT(*) AS estaciones "
            f"FROM precios WHERE combustible = ? AND fecha > ? AND estacion_id IN ({marcas}) "
            f"GROUP BY fecha ORDER BY fecha", (comb, _hace(hoy, dias), *ids)).fetchall()
    return [dict(f) for f in filas]


def por_dia_semana(serie: list[dict]) -> list[dict]:
    grupos: dict[int, list[float]] = {i: [] for i in range(7)}
    for f in serie:
        grupos[date.fromisoformat(f["fecha"]).weekday()].append(f["media"])
    """Media de cada día de la semana (0 = lunes)."""
    return [{"dia": i, "media": sum(v) / len(v) if v else None, "dias": len(v)} for i, v in grupos.items()]


def estacion(estacion_id: int) -> dict | None:
    with db.sesion() as con:
        fila = con.execute("SELECT * FROM estaciones WHERE id = ?", (estacion_id,)).fetchone()
    return dict(fila) if fila else None


def precios_actuales(estacion_id: int) -> dict[str, float]:
    """Último precio de cada combustible, solo si es del último día con datos."""
    with db.sesion() as con:
        filas = con.execute(
            """SELECT p.combustible, p.precio FROM precios p
               JOIN (SELECT combustible, MAX(fecha) AS fecha FROM precios GROUP BY combustible) u
                 ON u.combustible = p.combustible AND u.fecha = p.fecha
               WHERE p.estacion_id = ?""", (estacion_id,)).fetchall()
    return {f["combustible"]: f["precio"] for f in filas}


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

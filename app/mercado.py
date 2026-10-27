"""Precio del petróleo (Brent), del gasóleo y la gasolina al por mayor, y cambio euro/dólar,
para saber hacia dónde va el surtidor.

Brent, gasóleo y gasolina: FRED (St. Louis Fed), que republica las series diarias de la EIA de
EE. UU. (dominio público) con cerca de una semana de retraso. El gasóleo y la gasolina son los
del puerto de Nueva York: en España no hay una serie diaria abierta, pero se mueven con el
mercado mundial y adelantan el surtidor mejor que el crudo (ver prediccion.py). Euro/dólar: el BCE (reutilización libre citando
la fuente). Todo público, sin registro y con permiso para usarlo en una web abierta.
"""
from __future__ import annotations

import csv
import io
import logging
import urllib.request
from datetime import date, timedelta

from . import cache, db

log = logging.getLogger("pumpcast")

FRED = "https://fred.stlouisfed.org/graph/fredgraph.csv?id={}&cosd={}"
BRENT = "DCOILBRENTEU"
# Columna de la tabla mercado -> serie de FRED, en dólares por galón.
PRODUCTOS = {"gasoil_usd": "DDFUELNYH", "gasolina_usd": "DGASNYH"}
# Qué mercado sigue cada combustible. Los gases (GLP, GNC, GNL) no tienen serie abierta: el Brent.
REFERENCIA = {"g95": "gasolina", "g98": "gasolina", "diesel": "gasoil", "diesel_plus": "gasoil"}
LITROS_POR_GALON = 3.78541
BCE = ("https://data-api.ecb.europa.eu/service/data/EXR/D.USD.EUR.SP00.A"
       "?format=csvdata&startPeriod={}")


def _leer(url: str) -> str:
    peticion = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (pumpcast)"})
    with urllib.request.urlopen(peticion, timeout=60) as respuesta:
        return respuesta.read().decode()


def brent_fred(texto: str) -> dict[str, float]:
    filas = csv.reader(io.StringIO(texto))
    next(filas, None)
    return {f[0]: float(f[1]) for f in filas if len(f) == 2 and f[1] not in ("", ".")}


def eurusd_bce(texto: str) -> dict[str, float]:
    return {f["TIME_PERIOD"]: float(f["OBS_VALUE"]) for f in csv.DictReader(io.StringIO(texto))
            if f.get("OBS_VALUE")}


def descargar(dias: int = 730) -> tuple[dict[str, float], dict[str, float], dict[str, dict[str, float]]]:
    """Brent, euro/dólar y los productos. Si falla un producto, se sigue sin él (la previsión de
    ese combustible usa el Brent); si falla el Brent o el euro/dólar, no se guarda nada."""
    desde = (date.today() - timedelta(days=dias)).isoformat()
    productos = {}
    for columna, serie in PRODUCTOS.items():
        try:
            productos[columna] = brent_fred(_leer(FRED.format(serie, desde)))
        except Exception as e:  # noqa: BLE001
            log.warning("No se pudo leer %s de FRED: %s", serie, e)
    return brent_fred(_leer(FRED.format(BRENT, desde))), eurusd_bce(_leer(BCE.format(desde))), productos


def _guardar_serie(con, columna: str, valores: dict[str, float]) -> None:
    con.executemany(f"INSERT INTO mercado (fecha, {columna}) VALUES (?, ?) "
                    f"ON CONFLICT(fecha) DO UPDATE SET {columna} = excluded.{columna}", valores.items())
    if valores:                    # lo que quedara de otra fuente más allá del último dato de FRED
        con.execute(f"UPDATE mercado SET {columna} = NULL WHERE fecha > ?", (max(valores),))


def guardar(brent: dict[str, float], eurusd: dict[str, float],
            productos: dict[str, dict[str, float]] | None = None) -> None:
    with db.sesion() as con:
        _guardar_serie(con, "brent_usd", brent)
        for columna, valores in (productos or {}).items():
            if columna in PRODUCTOS:
                _guardar_serie(con, columna, valores)
        con.executemany(
            "INSERT INTO mercado (fecha, eurusd) VALUES (?, ?) "
            "ON CONFLICT(fecha) DO UPDATE SET eurusd = excluded.eurusd", eurusd.items())
    cache.invalidar()


DIAS_SIN_BRENT = 14         # FRED va una semana tarde; el doble ya es que algo se ha roto


def ultimo_brent() -> str | None:
    with db.sesion() as con:
        return con.execute("SELECT MAX(fecha) FROM mercado WHERE brent_usd IS NOT NULL").fetchone()[0]


def ultimos_productos() -> dict[str, str | None]:
    """El último día publicado del gasóleo y la gasolina ({"gasoil": "2026-10-20", ...})."""
    with db.sesion() as con:
        return {c.removesuffix("_usd"): con.execute(f"SELECT MAX(fecha) FROM mercado WHERE {c} IS NOT NULL").fetchone()[0]
                for c in PRODUCTOS}


def brent_viejo(ultimo: str | None, hoy: date | None = None) -> bool:
    """Si el Brent lleva demasiado sin llegar. Sin ninguno aún (recién instalada), no avisa."""
    return ultimo is not None and (hoy or date.today()) - date.fromisoformat(ultimo) > timedelta(days=DIAS_SIN_BRENT)


def _en_euros(columna: str, divisor: float = 1.0) -> dict[str, float]:
    """La columna en euros (entre `divisor`) para cada día natural hasta el último publicado,
    rellenando fines de semana y festivos con el último valor conocido."""
    with db.sesion() as con:
        ultimo = con.execute(f"SELECT MAX(fecha) FROM mercado WHERE {columna} IS NOT NULL").fetchone()[0]
        filas = con.execute(f"SELECT fecha, {columna} AS valor, eurusd FROM mercado WHERE fecha <= ? ORDER BY fecha",
                            (ultimo or "",)).fetchall()
    if not filas:
        return {}
    serie, valor, cambio = {}, None, None
    dia, fin = date.fromisoformat(filas[0]["fecha"]), date.fromisoformat(filas[-1]["fecha"])
    por_fecha = {f["fecha"]: f for f in filas}
    while dia <= fin:
        f = por_fecha.get(dia.isoformat())
        if f:
            valor = f["valor"] or valor
            cambio = f["eurusd"] or cambio
        if valor and cambio:
            serie[dia.isoformat()] = valor / cambio / divisor
        dia += timedelta(days=1)
    return serie


def brent_euros() -> dict[str, float]:
    """Brent en euros por barril, día a día."""
    return _en_euros("brent_usd")


def series() -> dict[str, dict[str, float]]:
    """Todo lo que usa la previsión: el Brent en euros por barril y los productos en euros por litro."""
    return {"brent": brent_euros(),
            **{columna.removesuffix("_usd"): _en_euros(columna, LITROS_POR_GALON) for columna in PRODUCTOS}}

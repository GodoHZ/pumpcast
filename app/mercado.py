"""Precio del petróleo (Brent) y cambio euro/dólar, para saber hacia dónde va la gasolina.

Brent: Yahoo Finance (futuro BZ=F); si falla, FRED (St. Louis Fed), que va unos días
por detrás. Euro/dólar: el BCE. Todo público y sin registro.
"""
from __future__ import annotations

import csv
import io
import json
import urllib.request
from datetime import date, timedelta

from . import db

YAHOO = "https://query1.finance.yahoo.com/v8/finance/chart/BZ=F?range=2y&interval=1d"
FRED = "https://fred.stlouisfed.org/graph/fredgraph.csv?id=DCOILBRENTEU&cosd={}"
BCE = ("https://data-api.ecb.europa.eu/service/data/EXR/D.USD.EUR.SP00.A"
       "?format=csvdata&startPeriod={}")


def _leer(url: str) -> str:
    peticion = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (pumpcast)"})
    with urllib.request.urlopen(peticion, timeout=60) as respuesta:
        return respuesta.read().decode()


def brent_yahoo(texto: str) -> dict[str, float]:
    r = json.loads(texto)["chart"]["result"][0]
    cierres = r["indicators"]["quote"][0]["close"]
    return {date.fromtimestamp(t).isoformat(): c for t, c in zip(r["timestamp"], cierres) if c}


def brent_fred(texto: str) -> dict[str, float]:
    filas = csv.reader(io.StringIO(texto))
    next(filas, None)
    return {f[0]: float(f[1]) for f in filas if len(f) == 2 and f[1] not in ("", ".")}


def eurusd_bce(texto: str) -> dict[str, float]:
    return {f["TIME_PERIOD"]: float(f["OBS_VALUE"]) for f in csv.DictReader(io.StringIO(texto))
            if f.get("OBS_VALUE")}


def descargar(dias: int = 730) -> tuple[dict[str, float], dict[str, float]]:
    desde = (date.today() - timedelta(days=dias)).isoformat()
    try:
        brent = brent_yahoo(_leer(YAHOO))
    except Exception:  # noqa: BLE001 - Yahoo no es una API oficial: si cambia, tiramos de FRED
        brent = brent_fred(_leer(FRED.format(desde)))
    return brent, eurusd_bce(_leer(BCE.format(desde)))


def guardar(brent: dict[str, float], eurusd: dict[str, float]) -> None:
    with db.sesion() as con:
        con.executemany(
            "INSERT INTO mercado (fecha, brent_usd) VALUES (?, ?) "
            "ON CONFLICT(fecha) DO UPDATE SET brent_usd = excluded.brent_usd", brent.items())
        con.executemany(
            "INSERT INTO mercado (fecha, eurusd) VALUES (?, ?) "
            "ON CONFLICT(fecha) DO UPDATE SET eurusd = excluded.eurusd", eurusd.items())


def brent_euros() -> dict[str, float]:
    """Brent en euros por barril para cada día natural, rellenando fines de semana y festivos
    con el último valor conocido."""
    with db.sesion() as con:
        filas = con.execute("SELECT fecha, brent_usd, eurusd FROM mercado ORDER BY fecha").fetchall()
    if not filas:
        return {}
    serie, brent, cambio = {}, None, None
    dia, fin = date.fromisoformat(filas[0]["fecha"]), date.fromisoformat(filas[-1]["fecha"])
    por_fecha = {f["fecha"]: f for f in filas}
    while dia <= fin:
        f = por_fecha.get(dia.isoformat())
        if f:
            brent = f["brent_usd"] or brent
            cambio = f["eurusd"] or cambio
        if brent and cambio:
            serie[dia.isoformat()] = brent / cambio
        dia += timedelta(days=1)
    return serie

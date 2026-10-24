"""SQLite: una conexión por operación, que la app es pequeña y así no hay sorpresas entre hilos."""
from __future__ import annotations

import sqlite3
from contextlib import contextmanager

from . import config

ESQUEMA = """
CREATE TABLE IF NOT EXISTS estaciones (
    id        INTEGER PRIMARY KEY,          -- IDEESS del Ministerio
    rotulo    TEXT NOT NULL,
    direccion TEXT,
    localidad TEXT,
    municipio TEXT,
    provincia TEXT,
    cp        TEXT,
    lat       REAL NOT NULL,
    lon       REAL NOT NULL,
    horario   TEXT,
    vista     TEXT NOT NULL                 -- última vez que apareció en una lectura
);
-- Un precio por estación, combustible y día: el último que se vio ese día.
CREATE TABLE IF NOT EXISTS precios (
    estacion_id INTEGER NOT NULL REFERENCES estaciones(id),
    combustible TEXT NOT NULL,
    fecha       TEXT NOT NULL,
    precio      REAL NOT NULL,
    PRIMARY KEY (estacion_id, combustible, fecha)
);
CREATE INDEX IF NOT EXISTS precios_por_fecha ON precios (combustible, fecha);
CREATE TABLE IF NOT EXISTS ajustes (
    clave TEXT PRIMARY KEY,
    valor TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS lecturas (
    momento     TEXT NOT NULL,
    fecha_datos TEXT,
    estaciones  INTEGER,
    error       TEXT
);
-- Avisos ya enviados, para no repetirlos (diario:2026-10-24, chollo:2026-10-24:1234...).
CREATE TABLE IF NOT EXISTS avisos (
    clave   TEXT PRIMARY KEY,
    momento TEXT NOT NULL
);
-- Días pasados ya descargados del histórico del Ministerio, por provincia.
CREATE TABLE IF NOT EXISTS historico (
    fecha     TEXT NOT NULL,
    provincia TEXT NOT NULL,
    PRIMARY KEY (fecha, provincia)
);
-- Brent en dólares por barril y dólares por euro, por día de mercado.
CREATE TABLE IF NOT EXISTS mercado (
    fecha     TEXT PRIMARY KEY,
    brent_usd REAL,
    eurusd    REAL
);
-- Lo que la previsión dijo cada día, para comprobar luego si acertó.
CREATE TABLE IF NOT EXISTS predicciones (
    fecha       TEXT NOT NULL,
    combustible TEXT NOT NULL,
    cambio      REAL NOT NULL,              -- euros por litro previstos a 7 días
    semaforo    TEXT NOT NULL,
    PRIMARY KEY (fecha, combustible)
);
"""


def conectar() -> sqlite3.Connection:
    config.DATA_DIR.mkdir(parents=True, exist_ok=True)
    con = sqlite3.connect(config.DB_PATH, timeout=30)
    con.row_factory = sqlite3.Row
    con.execute("PRAGMA foreign_keys = ON")
    return con


@contextmanager
def sesion():
    con = conectar()
    try:
        with con:
            yield con
    finally:
        con.close()


def iniciar() -> None:
    con = conectar()
    try:
        con.execute("PRAGMA journal_mode = WAL")
        con.executescript(ESQUEMA)
    finally:
        con.close()

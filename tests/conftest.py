"""Los tests usan una lectura real de Madrid centro (tests/datos/madrid.json) y una base de datos temporal."""
import json
import os
import tempfile
from datetime import timedelta
from pathlib import Path

os.environ["DATA_DIR"] = tempfile.mkdtemp(prefix="pumpcast-tests-")
os.environ["SIN_TAREAS"] = "1"
os.environ["PROVINCIAS"] = "28"
os.environ.pop("TELEGRAM_TOKEN", None)
os.environ.pop("TELEGRAM_CHAT", None)

import pytest  # noqa: E402

from app import config, db, minetur, repo  # noqa: E402

DATOS = json.loads((Path(__file__).parent / "datos" / "madrid.json").read_text(encoding="utf-8"))
SOL = {"lat": "40.4168", "lon": "-3.7038"}                  # la casa de los tests: la Puerta del Sol


@pytest.fixture(autouse=True)
def base_limpia():
    if config.DB_PATH.exists():
        config.DB_PATH.unlink()
    db.iniciar()
    repo.guardar_ajustes(SOL)
    yield


@pytest.fixture
def lectura():
    """La lectura real interpretada: (momento, estaciones)."""
    return minetur.interpretar(DATOS)


@pytest.fixture
def una(lectura):
    """Una estación con precio de gasolina 95, para los tests que necesitan una concreta."""
    return next(e for e in lectura[1] if "g95" in e["precios"])


@pytest.fixture
def cargada(lectura):
    repo.guardar_lectura(*lectura)
    return lectura


@pytest.fixture
def con_historial(lectura):
    """Diez días anteriores con todo 10 céntimos más caro, y luego la lectura de hoy."""
    momento, estaciones = lectura
    for dias in range(10, 0, -1):
        caras = [{**e, "precios": {c: p + 0.10 for c, p in e["precios"].items()}} for e in estaciones]
        repo.guardar_lectura(momento - timedelta(days=dias), caras)
    repo.guardar_lectura(momento, estaciones)
    return lectura

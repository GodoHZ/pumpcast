"""Una copia de la base de datos al día, si COPIAS_DIR apunta a una carpeta.

La carpeta tiene que existir ya y tener dentro un fichero «.pumpcast-copias» (créalo una vez a
mano). Si no está, no se escribe nada: así, con el disco sin montar, las copias no acaban
escondidas en el disco del sistema bajo un punto de montaje vacío (Docker crea la carpeta vacía). Cada copia se
comprueba con integrity_check y se guardan las de los últimos DIAS_DE_COPIAS días.
"""
from __future__ import annotations

import logging
import sqlite3
from datetime import date

from . import config, db

log = logging.getLogger("pumpcast")

MARCA = ".pumpcast-copias"
_ultima: date | None = None


def hacer(hoy: date) -> bool:
    """La copia del día, si toca. Devuelve si la ha hecho."""
    global _ultima
    carpeta = config.COPIAS_DIR
    if carpeta is None or _ultima == hoy:
        return False
    if not (carpeta / MARCA).is_file():
        log.warning("No hay copia: falta %s (¿el disco está montado?)", carpeta / MARCA)
        _ultima = hoy
        return False
    destino = carpeta / f"pumpcast-{hoy.isoformat()}.db"
    _ultima = hoy
    if destino.exists():
        return False
    temporal = destino.with_suffix(".tmp")
    origen = db.conectar()
    try:
        copia = sqlite3.connect(temporal)
        with copia:
            origen.backup(copia)
        bien = copia.execute("PRAGMA integrity_check").fetchone()[0] == "ok"
        copia.close()
    finally:
        origen.close()
    if not bien:
        temporal.unlink(missing_ok=True)
        log.warning("La copia de %s no ha pasado la comprobación: se descarta", hoy)
        return False
    temporal.replace(destino)
    for vieja in sorted(carpeta.glob("pumpcast-*.db"))[:-config.DIAS_DE_COPIAS]:
        vieja.unlink()
    log.info("Copia de la base de datos: %s", destino.name)
    return True

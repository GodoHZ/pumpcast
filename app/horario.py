"""Si una gasolinera está abierta ahora, según el horario que publica el Ministerio.

El formato es como «L-V: 06:00-22:00; S: 07:00-15:00 y 17:00-21:00; D: 24H». Lo que no se
entiende (o un horario de un solo día, que suele ser un dato a medias) se da por desconocido:
la gasolinera sale igual, sin decir si está abierta. Los festivos no se publican.
"""
from __future__ import annotations

import re
from functools import lru_cache
from datetime import datetime
from zoneinfo import ZoneInfo

DIAS = "LMXJVSD"
CANARIAS = ZoneInfo("Atlantic/Canary")
PROVINCIAS_CANARIAS = ("35", "38")
_TRAMO = re.compile(r"^(\d{1,2}):(\d{2})-(\d{1,2}):(\d{2})$")


@lru_cache(maxsize=8192)                  # se repiten mucho («L-D: 24H»...): no hace falta leerlos cada vez
def interpretar(texto: str | None) -> dict[int, list[tuple[int, int]]] | None:
    """Minutos de apertura de cada día de la semana (0 = lunes), o None si no se entiende."""
    if not texto:
        return None
    semana: dict[int, list[tuple[int, int]]] = {}
    for parte in texto.split(";"):
        dias, _, horas = parte.strip().partition(":")
        dias, horas = dias.strip().upper(), horas.strip().upper()
        if re.fullmatch(r"[LMXJVSD]", dias):
            lista = [DIAS.index(dias)]
        elif re.fullmatch(r"[LMXJVSD]-[LMXJVSD]", dias):
            ini, fin = DIAS.index(dias[0]), DIAS.index(dias[2])
            lista = list(range(ini, fin + 1)) if ini <= fin else [*range(ini, 7), *range(0, fin + 1)]
        else:
            return None
        tramos = []
        for tramo in horas.split(" Y "):
            tramo = tramo.strip()
            if tramo == "24H":
                tramos.append((0, 24 * 60))
                continue
            m = _TRAMO.match(tramo)
            if not m:
                return None
            h1, m1, h2, m2 = map(int, m.groups())
            fin = h2 * 60 + m2
            if fin in (0, 23 * 60 + 59):                   # «-00:00» y «-23:59» son hasta medianoche
                fin = 24 * 60
            tramos.append((h1 * 60 + m1, fin))
        for d in lista:
            semana.setdefault(d, []).extend(tramos)
    return semana if len(semana) > 1 else None


def hora_local(ahora: datetime, provincia_id: str | None) -> datetime:
    """Canarias va una hora por detrás, y su horario está en su hora."""
    return ahora.astimezone(CANARIAS) if provincia_id in PROVINCIAS_CANARIAS else ahora


def _abierta_en(semana: dict, dia: int, minuto: int) -> tuple[bool, int | None]:
    """Si está abierta ese día a ese minuto y, si lo está, a qué minuto cierra."""
    for ini, fin in semana.get(dia, []):
        if fin <= ini:                                     # cruza la medianoche (22:00-06:00)
            if minuto >= ini:
                return True, fin + 24 * 60
        elif ini <= minuto < fin:
            return True, fin
    for ini, fin in semana.get((dia - 1) % 7, []):        # lo que viene de la noche anterior
        if fin <= ini and minuto < fin:
            return True, fin
    return False, None


def estado(texto: str | None, ahora: datetime, provincia_id: str | None = None) -> dict | None:
    """{"abierta": bool, "clave": "24h" | "cierra" | "abre" | "cerrada", "hora": "22:00"},
    o None si el horario no se entiende."""
    semana = interpretar(texto)
    if semana is None:
        return None
    ahora = hora_local(ahora, provincia_id)
    dia, minuto = ahora.weekday(), ahora.hour * 60 + ahora.minute
    if all(semana.get(d) == [(0, 24 * 60)] for d in range(7)):
        return {"abierta": True, "clave": "24h", "hora": None}
    abierta, cierra = _abierta_en(semana, dia, minuto)
    if abierta:
        cierra %= 24 * 60
        return {"abierta": True, "clave": "cierra", "hora": f"{cierra // 60:02d}:{cierra % 60:02d}"}
    abre = min((ini for ini, fin in semana.get(dia, []) if ini > minuto), default=None)
    if abre is not None:
        return {"abierta": False, "clave": "abre", "hora": f"{abre // 60:02d}:{abre % 60:02d}"}
    return {"abierta": False, "clave": "cerrada", "hora": None}


def abierta(e: dict, ahora: datetime) -> bool:
    """Para elegir la más barata: lo que no se sabe cuenta como abierto."""
    est = estado(e.get("horario"), ahora, e.get("provincia_id"))
    return est is None or est["abierta"]

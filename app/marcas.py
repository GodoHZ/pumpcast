"""El distintivo de cada marca en el mapa: sus iniciales sobre su color.

No se usan los logos (son marcas registradas y sus dibujos tienen derechos de autor): solo las
iniciales y un color parecido al suyo, que no es de nadie. Las marcas que no están aquí reciben un
color sacado de su nombre, siempre el mismo.
"""
from __future__ import annotations

import hashlib
from functools import lru_cache

# rótulo del Ministerio -> (iniciales, color de fondo)
CONOCIDAS = {
    "REPSOL": ("R", "#ef7d00"), "CAMPSA": ("C", "#d52b1e"), "PETRONOR": ("P", "#00703c"),
    "CEPSA": ("C", "#d8282f"), "MOEVE": ("M", "#00a19a"), "GALP": ("G", "#f15a22"),
    "BP": ("BP", "#007f3e"), "SHELL": ("S", "#fbce07"), "BALLENOIL": ("B", "#0072bc"),
    "PLENERGY": ("P", "#e2001a"), "PETROPRIX": ("P", "#1d4f91"), "CARREFOUR": ("C", "#004e9f"),
    "ALCAMPO": ("A", "#e30613"), "EROSKI": ("E", "#e2001a"), "BONAREA": ("B", "#5a9a2a"),
    "AVIA": ("A", "#c8102e"), "Q8": ("Q8", "#1f3e93"), "ESCLATOIL": ("E", "#e85d1f"),
    "AGLA": ("A", "#00843d"), "VALCARCE": ("V", "#2b6cb0"), "ENI": ("E", "#f6c700"),
    "DISA": ("D", "#e30613"), "TAMOIL": ("T", "#d0021b"), "MEROIL": ("M", "#0057a8"),
    "BEROIL": ("B", "#00953b"), "GASEXPRESS": ("G", "#0099d8"), "PETROCAT": ("P", "#e4002b"),
}
SIN_MARCA = {"", "(SIN RÓTULO)", "SIN ROTULO", "SIN RÓTULO", "LIBRE"}
NEUTRO = "#6b7280"


def _tinta(fondo: str) -> str:
    """Letra blanca o casi negra, la que se lea mejor sobre ese fondo."""
    r, g, b = (int(fondo[i:i + 2], 16) for i in (1, 3, 5))
    return "#111827" if 0.299 * r + 0.587 * g + 0.114 * b > 165 else "#ffffff"


@lru_cache(maxsize=4096)
def insignia(rotulo: str | None) -> dict:
    """{"marca": "REPSOL", "texto": "R", "fondo": "#ef7d00", "tinta": "#ffffff"}."""
    marca = " ".join((rotulo or "").upper().split())
    if marca in CONOCIDAS:
        texto, fondo = CONOCIDAS[marca]
    elif marca in SIN_MARCA:
        texto, fondo = "·", NEUTRO
    else:
        letras = [p[0] for p in marca.replace("-", " ").split() if p[0].isalnum()]
        texto = (letras[0] if letras else "·")
        tono = int(hashlib.md5(marca.encode()).hexdigest()[:4], 16) % 360     # siempre el mismo
        fondo = _hsl_a_hex(tono, 0.45, 0.42)
    return {"marca": marca or "—", "texto": texto, "fondo": fondo, "tinta": _tinta(fondo)}


def _hsl_a_hex(h: float, s: float, l: float) -> str:
    c = (1 - abs(2 * l - 1)) * s
    x = c * (1 - abs((h / 60) % 2 - 1))
    m = l - c / 2
    r, g, b = [(c, x, 0), (x, c, 0), (0, c, x), (0, x, c), (x, 0, c), (c, 0, x)][int(h // 60) % 6]
    return "#" + "".join(f"{round((v + m) * 255):02x}" for v in (r, g, b))

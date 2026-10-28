#!/usr/bin/env python3
"""Dibuja los iconos de la app (PNG) sin librerías externas.

El mismo surtidor que app/static/iconos/icono.svg, en una rejilla de 64x64, sobre el
degradado de la paleta Glaciar (de --gds-cielo arriba a la izquierda a --gds-glaciar abajo a la derecha). Se ejecuta a mano y los PNG van en el repositorio:
    python3 scripts/make_icons.py
"""
from __future__ import annotations

import math
import struct
import zlib
from pathlib import Path

ICONOS = Path(__file__).resolve().parent.parent / "app" / "static" / "iconos"
CIELO = (56, 189, 248)         # --gds-cielo del CSS
GLACIAR = (2, 118, 181)        # --gds-glaciar
BLANCO = (255, 255, 255)
MUESTRAS = 4                   # muestras por lado y píxel (suavizado)


def escribir_png(ruta: Path, pixeles: list[list[tuple[int, int, int, int]]]) -> None:
    alto, ancho = len(pixeles), len(pixeles[0])
    crudo = bytearray()
    for fila in pixeles:
        crudo.append(0)                                   # filtro "None"
        for r, g, b, a in fila:
            crudo += bytes((r, g, b, a))

    def trozo(tipo: bytes, datos: bytes) -> bytes:
        return (struct.pack(">I", len(datos)) + tipo + datos
                + struct.pack(">I", zlib.crc32(tipo + datos) & 0xFFFFFFFF))

    ruta.write_bytes(b"\x89PNG\r\n\x1a\n"
                     + trozo(b"IHDR", struct.pack(">IIBBBBB", ancho, alto, 8, 6, 0, 0, 0))
                     + trozo(b"IDAT", zlib.compress(bytes(crudo), 9))
                     + trozo(b"IEND", b""))


def rectangulo(x: float, y: float, x0: float, y0: float, x1: float, y1: float, radio: float = 0) -> bool:
    if not (x0 <= x <= x1 and y0 <= y <= y1):
        return False
    cx = min(max(x, x0 + radio), x1 - radio)
    cy = min(max(y, y0 + radio), y1 - radio)
    return (x - cx) ** 2 + (y - cy) ** 2 <= radio ** 2


def _manguera() -> list[tuple[float, float]]:
    """El tubo del surtidor como una línea de puntos (el path del SVG)."""
    puntos = [(38, 24), (42, 24)]
    puntos += [(42 + 3 * math.sin(a), 27 - 3 * math.cos(a)) for a in (i * math.pi / 2 / 8 for i in range(1, 9))]
    puntos += [(45, 44)]
    puntos += [(47.5 - 2.5 * math.cos(a), 44 + 2.5 * math.sin(a)) for a in (i * math.pi / 12 for i in range(1, 13))]
    puntos += [(50, 22), (45, 17)]
    return puntos


MANGUERA = _manguera()


def cerca_de_linea(x: float, y: float, puntos: list[tuple[float, float]], grosor: float) -> bool:
    for (ax, ay), (bx, by) in zip(puntos, puntos[1:]):
        dx, dy = bx - ax, by - ay
        t = max(0.0, min(1.0, ((x - ax) * dx + (y - ay) * dy) / (dx * dx + dy * dy)))
        if (x - ax - t * dx) ** 2 + (y - ay - t * dy) ** 2 <= (grosor / 2) ** 2:
            return True
    return False


def surtidor(x: float, y: float) -> bool:
    """¿Es blanco este punto de la rejilla de 64x64?"""
    if rectangulo(x, y, 20, 19, 34, 29, 1.5):            # la ventanita, del color del fondo
        return False
    return (rectangulo(x, y, 16, 14, 38, 52, 3) or rectangulo(x, y, 12, 50, 42, 54, 2)
            or cerca_de_linea(x, y, MANGUERA, 3))


def dibujar(lado: int, escala: float = 1.0, redondeado: bool = True) -> list[list[tuple]]:
    """escala < 1 encoge el dibujo hacia el centro (zona segura de los iconos recortables)."""
    filas = []
    for py in range(lado):
        fila = []
        for px in range(lado):
            fondo = blanco = 0
            for sy in range(MUESTRAS):
                for sx in range(MUESTRAS):
                    x = (px + (sx + 0.5) / MUESTRAS) * 64 / lado
                    y = (py + (sy + 0.5) / MUESTRAS) * 64 / lado
                    if redondeado and not rectangulo(x, y, 0, 0, 64, 64, 14):
                        continue
                    fondo += 1
                    gx, gy = 32 + (x - 32) / escala, 33 + (y - 33) / escala
                    blanco += surtidor(gx, gy)
            total = MUESTRAS * MUESTRAS
            if not fondo:
                fila.append((0, 0, 0, 0))
                continue
            mezcla = blanco / fondo
            t = (px + py) / (2 * lado)                    # el degradado, en diagonal
            base = tuple(c + (g - c) * t for c, g in zip(CIELO, GLACIAR))
            color = tuple(round(v + (b - v) * mezcla) for v, b in zip(base, BLANCO))
            fila.append((*color, round(255 * fondo / total)))
        filas.append(fila)
    return filas


def main() -> None:
    ICONOS.mkdir(parents=True, exist_ok=True)
    trabajos = [
        ("icono-192.png", 192, 1.0, True),
        ("icono-512.png", 512, 1.0, True),
        ("icono-recortable-512.png", 512, 0.75, False),
        ("apple-touch-icon.png", 180, 0.9, False),       # iOS ya le pone él las esquinas
    ]
    for nombre, lado, escala, redondeado in trabajos:
        escribir_png(ICONOS / nombre, dibujar(lado, escala, redondeado))
        print("escrito", nombre, lado)


if __name__ == "__main__":
    main()

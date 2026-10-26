"""Lo que sale igual para todos hasta que llegan datos nuevos (precios cercanos, la serie de una
zona, la previsión de una provincia) se calcula una vez y se guarda en memoria. Cada vez que se
guardan precios, histórico o Brent, se tira todo y se vuelve a calcular a la primera visita.
"""
from __future__ import annotations

from typing import Any, Callable

MAXIMO = 4000                     # entradas; si se llena, se vacía entera (es solo una caché)
_datos: dict[tuple, Any] = {}


def recordar(clave: tuple, calcular: Callable[[], Any]) -> Any:
    try:
        return _datos[clave]
    except KeyError:
        valor = calcular()
        if len(_datos) >= MAXIMO:
            _datos.clear()
        _datos[clave] = valor
        return valor


def invalidar() -> None:
    _datos.clear()

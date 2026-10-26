"""Cómo se escriben los números: con coma decimal en las lenguas de España y punto en inglés."""
from __future__ import annotations

from datetime import datetime


def numero(valor: float, decimales: int, lang: str = "es") -> str:
    texto = f"{valor:,.{decimales}f}"
    if lang != "en":
        texto = texto.replace(",", " ").replace(".", ",").replace(" ", ".")
    return texto


def euros(valor: float | None, decimales: int = 3, lang: str = "es") -> str:
    """Solo la cifra: 1,606 / 1.606."""
    return "–" if valor is None else numero(valor, decimales, lang)


def moneda(valor: float | None, decimales: int = 2, lang: str = "es") -> str:
    """Con el símbolo donde toca: 4,59 € / €4.59."""
    if valor is None:
        return "–"
    cifra = numero(abs(valor), decimales, lang)
    signo = "−" if valor < 0 else ""
    return f"{signo}{cifra} €" if lang != "en" else f"{signo}€{cifra}"


def centimos(diferencia: float | None, lang: str = "es") -> str:
    """Diferencia en euros por litro, escrita en céntimos con signo: +3,2 / −1,0."""
    if diferencia is None:
        return "–"
    if round(diferencia * 1000) == 0:
        return numero(0, 1, lang)
    return ("+" if diferencia > 0 else "−") + numero(abs(diferencia) * 100, 1, lang)


def km(distancia: float, lang: str = "es") -> str:
    if distancia < 1:
        return f"{distancia * 1000:.0f} m"
    return f"{numero(distancia, 1, lang)} km"


def titulo(texto: str | None) -> str:
    return (texto or "").title()


def dia(texto: str | None, lang: str = "es") -> str:
    """Solo el día: 20/10 o Oct 20."""
    if not texto:
        return "–"
    fecha = datetime.fromisoformat(texto)
    return f"{fecha.day}/{fecha.month}" if lang != "en" else f"{fecha:%b} {fecha.day}"


def fecha_corta(texto: str | None, lang: str = "es") -> str:
    if not texto:
        return "–"
    fecha = datetime.fromisoformat(texto)
    return fecha.strftime("%d/%m %H:%M") if lang != "en" else fecha.strftime("%b %d, %H:%M")

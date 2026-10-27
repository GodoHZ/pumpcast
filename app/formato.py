"""Cómo se escriben los números: con coma decimal en las lenguas de España y punto en inglés."""
from __future__ import annotations

import re
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


def porcentaje(tanto_por_uno: float, lang: str = "es") -> str:
    """Un cambio con signo: +2,7 % / +2.7% / % +2,7 (en euskera el signo % va delante)."""
    cifra = ("+" if tanto_por_uno >= 0 else "−") + numero(abs(tanto_por_uno) * 100, 1, lang)
    return {"en": f"{cifra}%", "eu": f"% {cifra}"}.get(lang, f"{cifra} %")


def km(distancia: float, lang: str = "es") -> str:
    if distancia < 1:
        return f"{distancia * 1000:.0f} m"
    return f"{numero(distancia, 1, lang)} km"


PARTICULAS = {"DE", "DEL", "LA", "LAS", "LOS", "EL", "Y", "A", "EN", "AL", "I", "LES", "ELS", "DELS",   # cast. y cat.
              "DO", "DA", "DOS", "DAS", "E"}                                                       # gallego


def titulo(texto: str | None) -> str:
    """Rótulos y direcciones, que el Ministerio da en mayúsculas: «CALLE DE LA PAZ» -> «Calle de la
    Paz». Las siglas de dos letras (BP, Q8, GM) se quedan como están."""
    sueltas = (texto or "").split(" ")
    palabras = []
    for i, palabra in enumerate(sueltas):
        if palabra.upper() == "KM":
            palabras.append("km")
        elif re.fullmatch(r"[A-Z]{1,3}-[A-Z0-9]+|[IVX]{2,5}|[IVX]+,?", palabra) and (palabra != "I" or i == len(sueltas) - 1):
            palabras.append(palabra)                  # carreteras (N-II, AP-7) y números romanos
        elif i and palabra.upper() in PARTICULAS:
            palabras.append(palabra.lower())
        elif len(palabra) <= 2 and palabra.isupper():
            palabras.append(palabra)
        else:
            palabras.append(palabra.title())
    return " ".join(palabras)


def municipio(texto: str | None) -> str:
    """El Ministerio pone el artículo detrás: «Hospitalet de Llobregat (L')» -> «L'Hospitalet de
    Llobregat», «Palmas de Gran Canaria (Las)» -> «Las Palmas de Gran Canaria». Para decirlo en voz alta."""
    m = re.fullmatch(r"(.+?)\s*\(([^()]{1,4})\)", (texto or "").strip())
    if not m:
        return texto or ""
    nombre, articulo = m.groups()
    return f"{articulo}{nombre}" if articulo.endswith("'") else f"{articulo} {nombre}"


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

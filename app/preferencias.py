"""Lo que cada visitante elige en Ajustes: dónde buscar, el radio, el combustible, los litros y el
idioma. Va en una cookie de su navegador; el servidor la lee para pintar la página y no la
apunta en ningún sitio. Así cada uno ve lo suyo y nadie ve lo de los demás.
"""
from __future__ import annotations

import re
import urllib.parse

from fastapi import Request

from . import config, i18n

COOKIE = "pumpcast"
DIAS_DE_COOKIE = 400


def validar(valores: dict, campos: tuple[str, ...]) -> tuple[dict, str | None]:
    """Limpia lo que llega de un formulario o una cookie. Devuelve los valores y, si algo está
    mal, la clave del error (en i18n). Sirve para las preferencias y para el panel."""
    v = {k: str(valores.get(k, "")).strip().replace(",", ".") for k in campos}
    try:
        lat, lon = float(v["lat"]), float(v["lon"])
        if not (-90 <= lat <= 90 and -180 <= lon <= 180):
            return v, "err.ubicacion"
        if not (config.ESPANA["lat"][0] <= lat <= config.ESPANA["lat"][1]
                and config.ESPANA["lon"][0] <= lon <= config.ESPANA["lon"][1]):
            return v, "err.fuera"
        v["lat"], v["lon"] = f"{lat:.5f}", f"{lon:.5f}"
        if not 1 <= float(v["radio_km"]) <= config.MAX_RADIO_KM:
            return v, "err.radio"
        if not 1 <= float(v["litros"]) <= 150:
            return v, "err.litros"
        v["radio_km"], v["litros"] = f"{float(v['radio_km']):g}", f"{float(v['litros']):g}"
        if "consumo" in v:
            v["consumo"] = v["consumo"] or config.PREFERENCIAS_POR_DEFECTO["consumo"]
            if not 1 <= float(v["consumo"]) <= 40:
                return v, "err.consumo"
            v["consumo"] = f"{float(v['consumo']):g}"
        if "umbral_chollo" in v and not 0 <= float(v["umbral_chollo"]) <= 1:
            return v, "err.umbral"
    except ValueError:
        return v, "err.numero"
    if "hora_aviso" in v and not re.fullmatch(r"([01]\d|2[0-3]):[0-5]\d", v["hora_aviso"]):
        return v, "err.hora"
    if v["combustible"] not in config.COMBUSTIBLES:
        return v, "err.combustible"
    # Lo que no pide escribir nada se arregla en vez de dar error (y así valen las cookies de antes).
    if "orden" in v and v["orden"] not in config.ORDENES:
        v["orden"] = config.PREFERENCIAS_POR_DEFECTO["orden"]
    if "tema" in v and v["tema"] not in config.TEMAS:
        v["tema"] = config.PREFERENCIAS_POR_DEFECTO["tema"]
    if "mapa" in v and v["mapa"] not in config.APPS_MAPAS:
        v["mapa"] = config.PREFERENCIAS_POR_DEFECTO["mapa"]
    if "gps" in v:
        v["gps"] = "1" if v["gps"] in ("1", "on") else "0"            # una casilla sin marcar no llega
    idiomas = (*i18n.IDIOMAS, "auto") if "hora_aviso" not in v else i18n.IDIOMAS
    if v["idioma"] not in idiomas:
        return v, "err.idioma"
    return v, None


CAMPOS = tuple(config.PREFERENCIAS_POR_DEFECTO)


def leer(request: Request) -> dict | None:
    """Las preferencias de la cookie, o None si no hay (o están mal)."""
    return leer_texto(request.cookies.get(COOKIE))


def leer_texto(texto: str | None) -> dict | None:
    if not texto or len(texto) > 500:
        return None
    datos = {k: v[0] for k, v in urllib.parse.parse_qs(texto).items()}
    valores, error = validar({**config.PREFERENCIAS_POR_DEFECTO, **datos}, CAMPOS)
    return None if error else valores


def para_cookie(valores: dict) -> str:
    return urllib.parse.urlencode({k: valores.get(k, config.PREFERENCIAS_POR_DEFECTO[k]) for k in CAMPOS})


def guardar(respuesta, request: Request, valores: dict) -> None:
    respuesta.set_cookie(COOKIE, para_cookie(valores), max_age=DIAS_DE_COOKIE * 86400, path="/",
                         httponly=True, secure=request.url.scheme == "https", samesite="lax")


def olvidar(respuesta) -> None:
    respuesta.delete_cookie(COOKIE, path="/")
    respuesta.delete_cookie(COOKIE_FAVORITAS, path="/")


# --- Gasolineras favoritas: otra cookie, solo con sus números -----------------------------

COOKIE_FAVORITAS = "pumpcast_fav"


def favoritas(request: Request) -> list[int]:
    texto = request.cookies.get(COOKIE_FAVORITAS, "")[:300]
    ids = [int(x) for x in texto.split(".") if x.isdigit()]
    return list(dict.fromkeys(ids))[:config.MAX_FAVORITAS]


def guardar_favoritas(respuesta, request: Request, ids: list[int]) -> None:
    if not ids:
        respuesta.delete_cookie(COOKIE_FAVORITAS, path="/")
        return
    respuesta.set_cookie(COOKIE_FAVORITAS, ".".join(map(str, ids[:config.MAX_FAVORITAS])),
                         max_age=DIAS_DE_COOKIE * 86400, path="/", httponly=True,
                         secure=request.url.scheme == "https", samesite="lax")

"""Precios del Geoportal de carburantes del Ministerio. API pública, sin registro ni token."""
from __future__ import annotations

import json
import ssl
import urllib.request
from datetime import date, datetime

from . import config

BASE = "https://sedeaplicaciones.minetur.gob.es/ServiciosRESTCarburantes/PreciosCarburantes/"
URL = BASE + "EstacionesTerrestres/FiltroProvincia/{}"
URL_HISTORICO = BASE + "EstacionesTerrestresHist/FiltroProvincia/{:%d-%m-%Y}/{}"


def _numero(texto: str | None) -> float | None:
    texto = (texto or "").strip().replace(",", ".")
    return float(texto) if texto else None


# El servidor del Ministerio solo habla TLS 1.2 con AES256-GCM-SHA384 (sin ECDHE), que el
# OpenSSL de la imagen ya no ofrece por defecto. Se añade solo ese cifrado; el certificado
# se sigue comprobando igual.
_TLS = ssl.create_default_context()
_TLS.set_ciphers("DEFAULT:AES256-GCM-SHA384")


def _descargar(url: str) -> dict:
    peticion = urllib.request.Request(url, headers={"Accept": "application/json",
                                                    "User-Agent": f"pumpcast/{config.VERSION}"})
    with urllib.request.urlopen(peticion, timeout=90, context=_TLS) as respuesta:
        return json.load(respuesta)


def descargar(provincia: str) -> dict:
    return _descargar(URL.format(provincia))


def descargar_dia(provincia: str, dia: date) -> dict:
    """Los precios de un día pasado (los que había a las 00:00 de ese día)."""
    return _descargar(URL_HISTORICO.format(dia, provincia))


def interpretar(datos: dict) -> tuple[datetime, list[dict]]:
    """Devuelve la hora de los datos y las estaciones abiertas al público con algún precio."""
    momento = datetime.strptime(datos["Fecha"], "%d/%m/%Y %H:%M:%S")
    estaciones = []
    for e in datos.get("ListaEESSPrecio", []):
        # "R" son las de venta restringida (cooperativas, socios): no puedes repostar ahí.
        if e.get("Tipo Venta") != "P":
            continue
        lat, lon = _numero(e.get("Latitud")), _numero(e.get("Longitud (WGS84)"))
        if lat is None or lon is None:
            continue
        precios = {}
        for clave, campo in config.COMBUSTIBLES.items():
            precio = _numero(e.get(campo))
            if precio:
                precios[clave] = precio
        if not precios:
            continue
        estaciones.append({
            "id": int(e["IDEESS"]),
            "rotulo": (e.get("Rótulo") or "").strip() or "Sin nombre",
            "direccion": (e.get("Dirección") or "").strip().rstrip(",").strip(),
            "localidad": (e.get("Localidad") or "").strip(),
            "municipio": (e.get("Municipio") or "").strip(),
            "provincia": (e.get("Provincia") or "").strip(),
            "cp": (e.get("C.P.") or "").strip(),
            "lat": lat,
            "lon": lon,
            "horario": (e.get("Horario") or "").strip(),
            "precios": precios,
        })
    return momento, estaciones

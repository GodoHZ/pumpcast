"""Configuración: lo que viene del entorno (el contenedor) y los valores por defecto."""
from __future__ import annotations

import os
from pathlib import Path
from zoneinfo import ZoneInfo

VERSION = os.environ.get("APP_VERSION", "dev")
DATA_DIR = Path(os.environ.get("DATA_DIR", "data"))
DB_PATH = DATA_DIR / "pumpcast.db"
TZ = ZoneInfo(os.environ.get("TZ", "Europe/Madrid"))

APP_URL = os.environ.get("APP_URL", "").rstrip("/")
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN", "").strip()
TELEGRAM_CHAT = os.environ.get("TELEGRAM_CHAT", "").strip()
SIN_TAREAS = os.environ.get("SIN_TAREAS") == "1"       # en los tests no se descarga nada

MINUTOS_ENTRE_LECTURAS = 30                             # el Ministerio actualiza cada media hora
MINUTOS_TRAS_ERROR = 10
MAX_PROVINCIAS = 4

# clave interna -> campo en la API del Ministerio. Los nombres para mostrar están en i18n.
COMBUSTIBLES = {
    "g95": "Precio Gasolina 95 E5",
    "g98": "Precio Gasolina 98 E5",
    "diesel": "Precio Gasoleo A",
    "diesel_plus": "Precio Gasoleo Premium",
    "glp": "Precio Gases licuados del petróleo",
}

# Código del Ministerio (el del INE), nombre y código ISO 3166-2 (el que da OpenStreetMap).
PROVINCIAS = [
    ("01", "Araba/Álava", "ES-VI"), ("02", "Albacete", "ES-AB"), ("03", "Alicante/Alacant", "ES-A"),
    ("04", "Almería", "ES-AL"), ("05", "Ávila", "ES-AV"), ("06", "Badajoz", "ES-BA"),
    ("07", "Illes Balears", "ES-PM"), ("08", "Barcelona", "ES-B"), ("09", "Burgos", "ES-BU"),
    ("10", "Cáceres", "ES-CC"), ("11", "Cádiz", "ES-CA"), ("12", "Castellón/Castelló", "ES-CS"),
    ("13", "Ciudad Real", "ES-CR"), ("14", "Córdoba", "ES-CO"), ("15", "A Coruña", "ES-C"),
    ("16", "Cuenca", "ES-CU"), ("17", "Girona", "ES-GI"), ("18", "Granada", "ES-GR"),
    ("19", "Guadalajara", "ES-GU"), ("20", "Gipuzkoa", "ES-SS"), ("21", "Huelva", "ES-H"),
    ("22", "Huesca", "ES-HU"), ("23", "Jaén", "ES-J"), ("24", "León", "ES-LE"),
    ("25", "Lleida", "ES-L"), ("26", "La Rioja", "ES-LO"), ("27", "Lugo", "ES-LU"),
    ("28", "Madrid", "ES-M"), ("29", "Málaga", "ES-MA"), ("30", "Murcia", "ES-MU"),
    ("31", "Navarra", "ES-NA"), ("32", "Ourense", "ES-OR"), ("33", "Asturias", "ES-O"),
    ("34", "Palencia", "ES-P"), ("35", "Las Palmas", "ES-GC"), ("36", "Pontevedra", "ES-PO"),
    ("37", "Salamanca", "ES-SA"), ("38", "Santa Cruz de Tenerife", "ES-TF"), ("39", "Cantabria", "ES-S"),
    ("40", "Segovia", "ES-SG"), ("41", "Sevilla", "ES-SE"), ("42", "Soria", "ES-SO"),
    ("43", "Tarragona", "ES-T"), ("44", "Teruel", "ES-TE"), ("45", "Toledo", "ES-TO"),
    ("46", "Valencia/València", "ES-V"), ("47", "Valladolid", "ES-VA"), ("48", "Bizkaia", "ES-BI"),
    ("49", "Zamora", "ES-ZA"), ("50", "Zaragoza", "ES-Z"), ("51", "Ceuta", "ES-CE"),
    ("52", "Melilla", "ES-ML"),
]
CODIGOS_PROVINCIA = {codigo for codigo, _, _ in PROVINCIAS}
PROVINCIA_POR_ISO = {iso: codigo for codigo, _, iso in PROVINCIAS}

# Lo que se cambia desde Ajustes. Se guarda en la base de datos como texto.
# PROVINCIAS (variable de entorno) solo da el valor inicial; luego manda lo de Ajustes.
AJUSTES_POR_DEFECTO = {
    "provincias": ",".join(p.strip().zfill(2) for p in os.environ.get("PROVINCIAS", "").split(",")
                           if p.strip()),
    "lat": "40.4168",            # Puerta del Sol, hasta que pongas tu casa
    "lon": "-3.7038",
    "radio_km": "10",
    "combustible": "g95",
    "litros": "40",              # lo que sueles echar en cada repostaje
    "umbral_chollo": "0.05",     # euros por litro por debajo de la media de 30 días
    "hora_aviso": "08:30",
    "aviso_diario": "1",
    "avisos_chollo": "1",
    "idioma": "auto",            # auto = el del navegador
    "idioma_visto": "",          # el último idioma del navegador, para los avisos con «auto»
}

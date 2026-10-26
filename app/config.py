"""Configuración: lo que viene del entorno (el contenedor) y los valores por defecto."""
from __future__ import annotations

import os
from pathlib import Path
from zoneinfo import ZoneInfo

VERSION = os.environ.get("APP_VERSION", "dev")
DATA_DIR = Path(os.environ.get("DATA_DIR", "data"))
DB_PATH = DATA_DIR / "pumpcast.db"
# Copia diaria de la base de datos (opcional): mejor en otro disco que el de DATA_DIR.
COPIAS_DIR = Path(os.environ["COPIAS_DIR"]) if os.environ.get("COPIAS_DIR") else None
DIAS_DE_COPIAS = int(os.environ.get("DIAS_DE_COPIAS", "14"))
TZ = ZoneInfo(os.environ.get("TZ", "Europe/Madrid"))

APP_URL = os.environ.get("APP_URL", "").rstrip("/")
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN", "").strip()
TELEGRAM_CHAT = os.environ.get("TELEGRAM_CHAT", "").strip()
TELEGRAM_THREAD = os.environ.get("TELEGRAM_THREAD", "").strip()   # tema de un grupo con temas (opcional)
SIN_TAREAS = os.environ.get("SIN_TAREAS") == "1"       # en los tests no se descarga nada
# Hash de la contraseña del panel de administración (python -m app.seguridad hash).
# Sin él, el panel no existe.
ADMIN_PASSWORD_HASH = os.environ.get("ADMIN_PASSWORD_HASH", "").strip()
# Para el aviso legal: quién responde de la web y cómo escribirle (correo o URL). Opcionales; sin
# contacto, la página manda a las incidencias de GitHub.
TITULAR = os.environ.get("TITULAR", "").strip()
CONTACTO = os.environ.get("CONTACTO", "").strip()
REPOSITORIO = "https://github.com/GodoHZ/pumpcast"

MINUTOS_ENTRE_LECTURAS = 30                             # el Ministerio actualiza cada media hora
MINUTOS_TRAS_ERROR = 10
DIAS_CON_PRECIOS = 95        # precios de cada gasolinera; las medias por provincia se guardan siempre

# clave interna -> campo en la API del Ministerio. Los nombres para mostrar están en i18n.
COMBUSTIBLES = {
    "g95": "Precio Gasolina 95 E5",
    "g98": "Precio Gasolina 98 E5",
    "diesel": "Precio Gasoleo A",
    "diesel_plus": "Precio Gasoleo Premium",
    "glp": "Precio Gases licuados del petróleo",
    "gnc": "Precio Gas Natural Comprimido",
    "gnl": "Precio Gas Natural Licuado",
}
# El biometano es el mismo combustible para el coche: si una gasolinera solo tiene ese, cuenta.
ALTERNATIVAS = {"gnc": "Precio Biogas Natural Comprimido", "gnl": "Precio Biogas Natural Licuado"}

# El gas natural se vende por kilo; el resto, por litro.
UNIDADES = {"gnc": "kg", "gnl": "kg"}


def unidad(comb: str) -> str:
    return UNIDADES.get(comb, "L")


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
NOMBRE_PROVINCIA = {codigo: nombre for codigo, nombre, _ in PROVINCIAS}

# Hasta dónde llegan los precios del Ministerio: la península, Baleares, Canarias, Ceuta y Melilla.
ESPANA = {"lat": (27.0, 44.5), "lon": (-18.5, 4.6)}
MAX_RADIO_KM = 50

# Lo que cada visitante elige en Ajustes. Se guarda solo en su navegador (una cookie).
PREFERENCIAS_POR_DEFECTO = {
    "lat": "", "lon": "", "radio_km": "10", "combustible": "g95", "litros": "40", "idioma": "auto",
    "gps": "0",                    # "1": al abrir la app, buscar alrededor de donde estés en ese momento
    "orden": "precio",             # la lista de Cerca: "precio", "distancia" o "compensa"
    "consumo": "6",
    "tema": "auto",                # "auto" (el del móvil), "claro" u "oscuro"                # litros (o kilos) a los 100 km, para saber si compensa ir más lejos
}
ORDENES = ("precio", "distancia", "compensa")
TEMAS = ("auto", "claro", "oscuro")
RODEO = 1.3                        # la carretera es más larga que la línea recta
MAX_FAVORITAS = 20
# Las apps entre las que se elige al pulsar «Cómo llegar».
MAPAS = {
    "google": "https://www.google.com/maps/dir/?api=1&destination={lat},{lon}",
    "apple": "https://maps.apple.com/?daddr={lat},{lon}",
    "waze": "https://waze.com/ul?ll={lat},{lon}&navigate=yes",
}

# Los avisos de Telegram del dueño de la instalación, desde el panel de administración.
# Se guardan en la base de datos como texto.
AJUSTES_POR_DEFECTO = {
    "lat": "40.4168",            # Puerta del Sol, hasta que pongas tu casa
    "lon": "-3.7038",
    "radio_km": "10",
    "combustible": "g95",
    "litros": "40",              # lo que sueles echar en cada repostaje
    "umbral_chollo": "0.05",     # euros por litro por debajo de la media de 30 días
    "hora_aviso": "08:30",
    "aviso_diario": "1",
    "avisos_chollo": "1",
    "idioma": "es",              # el de los avisos
}

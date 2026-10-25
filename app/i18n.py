"""Textos en castellano e inglés.

Cada texto tiene una clave; los que llevan {huecos} se rellenan con t(..., hueco=valor).
Los que llevan HTML (<b>) se pintan con |safe en las plantillas, y solo reciben números
ya formateados, nunca texto que venga de fuera.
"""
from __future__ import annotations

IDIOMAS = ("es", "en")

TEXTOS: dict[str, dict[str, str]] = {
    "es": {
        "nav.cerca": "Cerca", "nav.mapa": "Mapa", "nav.tendencia": "Tendencia", "nav.ajustes": "Ajustes",
        "aria.combustible": "Combustible", "aria.secciones": "Secciones",
        "comb.g95": "Gasolina 95", "comb.g98": "Gasolina 98", "comb.diesel": "Diésel",
        "comb.diesel_plus": "Diésel+", "comb.glp": "GLP",

        "inicio.primera_vez": "Para empezar, elige tu provincia y dónde está tu casa.",
        "inicio.ir_ajustes": "Ir a Ajustes",
        "inicio.sin_precios": "Aún no hay precios de {comb} a menos de {radio} km de casa.",
        "inicio.sin_precios_nota": "Si acabas de arrancar la app, la primera lectura tarda un momento. "
                                   "Si no, amplía el radio en Ajustes.",
        "inicio.mas_barata": "La más barata a menos de {radio} km",
        "inicio.ahorro": "Llenar {litros} L aquí te cuesta <b>{coste}</b>: ahorras <b>{ahorro}</b> frente a la "
                         "media de la zona ({media}).",
        "inicio.resto": "El resto cerca de casa",
        "inicio.resto_nota": "{total} en total · céntimos frente a la media",
        "como_llegar": "Cómo llegar", "historial": "Historial",
        "actualizar": "Actualizar", "actualizar_ahora": "Actualizar ahora",
        "pie.datos": "Precios del Ministerio · datos de {fecha}",
        "pie.sin_leer": "Precios del Ministerio · sin leer todavía",

        "mapa.titulo": "Mapa", "mapa.aria": "Mapa de gasolineras",
        "mapa.leyenda": '<span class="barata">●</span> más barata · <span class="cara">●</span> más cara, '
                        "comparando las de tu radio. Toca una para ver su precio.",

        "estacion.de_casa": "{distancia} de casa",
        "estacion.ultimos": "{comb}, últimos 90 días",
        "estacion.sin_historico": "Todavía no hay histórico: la app guarda un precio al día y la gráfica "
                                  "sale en cuanto haya dos.",
        "estacion.no_existe": "Esa gasolinera no está en la base de datos.",
        "estacion.coste": "Llenar {litros} L de {comb} aquí: <b>{coste}</b>",
        "serie.esta": "Esta gasolinera", "serie.zona": "Media de la zona", "serie.media": "Media",
        "serie.minimo": "La más barata", "serie.brent": "Brent (€/barril)",

        "tend.sin_datos": "Aún no hay datos de {comb} en tu zona.",
        "tend.media_hoy": "Media hoy", "tend.vs7": "Vs. hace 7 días", "tend.vs30": "Vs. hace 30 días",
        "tend.cts": "cts",
        "tend.zona": "{comb} a menos de {radio} km",
        "tend.grafica_pronto": "La gráfica sale en cuanto haya dos días de datos. La app guarda un precio al día.",
        "tend.dia_titulo": "¿Qué día sale más barato?",
        "tend.dia_mejor": "De media, el <b>{dia}</b> es el día más barato para repostar en tu zona.",
        "tend.dia_faltan": "Hacen falta al menos dos semanas de datos para saberlo. Llevas {dias} días.",

        "prev.titulo": "¿Lleno hoy o espero?",
        "prev.brent": "El Brent está a {precio} el barril{cambio}.",
        "prev.brent_cambio": " ({cambio} % en una semana)",
        "prev.como": "La previsión mira cuánto se han movido el Brent y el precio de tu zona en la última "
                     "semana: el surtidor va detrás del petróleo y los precios tienen inercia.",
        "prev.prueba": "Probado con los últimos 60 días sin usarlos para aprender: habría acertado "
                       "<b>{aciertos} de {total}</b> veces ({pct} %), con un error medio de {error} céntimos.",
        "prev.seguimiento": "Desde que se apuntan: <b>{aciertos} de {total}</b> aciertos.",
        "prev.apuntando": "Se apunta cada previsión; en una semana empezará a verse si acierta de verdad.",
        "prev.aviso": "Es una pista, no una garantía: no prevé sustos como guerras, impuestos o puentes.",
        "prev.cargando": "Cargando el histórico de precios del Ministerio y del petróleo. Hacen falta unos "
                         "100 días de datos: llevas {dias}. Tarda menos de una hora la primera vez.",
        "sem.llena": "Llena ya", "sem.igual": "Da igual", "sem.espera": "Espera si puedes",
        "frase.llena": "Se espera que suba unos {cts} céntimos esta semana ({euros} más por depósito si esperas).",
        "frase.espera": "Se espera que baje unos {cts} céntimos esta semana ({euros} menos por depósito si esperas).",
        "frase.igual": "No se esperan cambios grandes esta semana.",

        "dia.0": "Lunes", "dia.1": "Martes", "dia.2": "Miércoles", "dia.3": "Jueves", "dia.4": "Viernes",
        "dia.5": "Sábado", "dia.6": "Domingo",
        "dia_frase.0": "lunes", "dia_frase.1": "martes", "dia_frase.2": "miércoles", "dia_frase.3": "jueves",
        "dia_frase.4": "viernes", "dia_frase.5": "sábado", "dia_frase.6": "domingo",

        "aj.titulo": "Ajustes", "aj.guardado": "Guardado.", "aj.guardar": "Guardar",
        "aj.prueba_ok": "Mensaje de prueba enviado. Mira Telegram.",
        "aj.prueba_error": "No se pudo enviar. Revisa TELEGRAM_TOKEN y TELEGRAM_CHAT.",
        "aj.casa": "Casa", "aj.buscar_ph": "Calle, número y pueblo", "aj.buscar": "Buscar",
        "aj.buscar_aria": "Buscar dirección", "aj.mapa_aria": "Mapa para colocar tu casa",
        "aj.mapa_ayuda": "Busca tu dirección, toca el mapa o arrastra la chincheta. Luego, Guardar.",
        "aj.mi_ubicacion": "📍 Usar mi ubicación", "aj.coordenadas": "Coordenadas a mano",
        "aj.latitud": "Latitud", "aj.longitud": "Longitud", "aj.radio": "Radio (km)",
        "aj.provincias": "Provincias",
        "aj.provincias_nota": "De dónde se leen los precios. Al buscar tu dirección se elige sola. "
                              "Puedes marcar hasta 4, por si vives cerca del límite.",
        "aj.coche": "Coche", "aj.combustible": "Combustible", "aj.litros": "Litros que sueles echar",
        "aj.avisos": "Avisos por Telegram",
        "aj.telegram_falta": "Telegram no está configurado: añade TELEGRAM_TOKEN y TELEGRAM_CHAT al contenedor.",
        "aj.resumen": "Resumen cada mañana", "aj.hora": "Hora del resumen",
        "aj.chollos": "Avisarme de chollos (de 8 a 22 h)",
        "aj.umbral": "Chollo = por debajo de la media de 30 días en (€/L)",
        "aj.idioma": "Idioma", "aj.idioma_auto": "El del navegador",
        "aj.enviar_prueba": "Enviar un mensaje de prueba",
        "aj.version": "Versión {version}", "aj.ultima": "última lectura {fecha}",

        "err.ubicacion": "La ubicación no es válida.",
        "err.radio": "El radio tiene que estar entre 1 y 100 km.",
        "err.litros": "Los litros por repostaje tienen que estar entre 1 y 150.",
        "err.umbral": "El umbral del chollo va en euros por litro, por ejemplo 0,05.",
        "err.numero": "Hay algún número mal escrito.",
        "err.hora": "La hora del aviso va como 08:30.",
        "err.combustible": "Ese combustible no existe.",
        "err.provincias": "Elige entre 1 y 4 provincias.",
        "err.idioma": "Ese idioma no está disponible.",
        "err.buscador": "El buscador de direcciones no responde. Prueba en un rato.",

        "js.casa": "Casa", "js.ver_historial": "Ver historial",
        "js.buscando": "Buscando…", "js.escribe_mas": "Escribe un poco más de la dirección.",
        "js.no_encontrada": "No he encontrado esa dirección. Prueba con calle y pueblo.",
        "js.elige": "Elige la buena:",
        "js.encontrada": "Dirección encontrada. Si no es justo tu portal, arrastra la chincheta.",
        "js.no_se_pudo_buscar": "No se pudo buscar: ", "js.movida": "Chincheta movida.",
        "js.tocado": "Casa puesta donde has tocado.", "js.coordenadas": "Coordenadas puestas.",
        "js.sin_gps": "Este navegador no da la ubicación.", "js.buscando_gps": "Buscando dónde estás…",
        "js.gps_ok": "Puesta tu ubicación actual.", "js.no_se_pudo": "No se pudo: ",
        "js.guardar": " Dale a Guardar.", "js.provincia": " Provincia: {p}.",

        "off.titulo": "Sin conexión",
        "off.texto": "No hay conexión y esta pantalla no estaba guardada. Ábrela una vez con conexión "
                     "y quedará disponible.",
        "off.aviso": "Sin conexión · datos del {fecha}",
        "manifest.descripcion": "Las gasolineras más baratas cerca de casa y si sale a cuenta llenar hoy.",

        "tg.hoy": "⛽ <b>{comb} hoy</b> a menos de {radio} km",
        "tg.media": "Media de la zona: {media}. Llenar {litros} L en la primera cuesta <b>{coste}</b> "
                    "y ahorras <b>{ahorro}</b>.",
        "tg.sube": "Sube {cts} céntimos desde hace una semana.",
        "tg.baja": "Baja {cts} céntimos desde hace una semana.",
        "tg.igual": "Igual que hace una semana.",
        "tg.chollo": "🔥 <b>Chollo</b>: {comb} a <b>{precio}</b> en {sitio}.\n"
                     "Son {cts} céntimos menos que la media de los últimos 30 días ({media}).",
        "tg.prueba": "✅ Prueba desde Pumpcast: los avisos llegan bien.",
    },
    "en": {
        "nav.cerca": "Nearby", "nav.mapa": "Map", "nav.tendencia": "Trends", "nav.ajustes": "Settings",
        "aria.combustible": "Fuel", "aria.secciones": "Sections",
        "comb.g95": "Petrol 95", "comb.g98": "Petrol 98", "comb.diesel": "Diesel",
        "comb.diesel_plus": "Diesel+", "comb.glp": "LPG",

        "inicio.primera_vez": "To get started, pick your province and where home is.",
        "inicio.ir_ajustes": "Open Settings",
        "inicio.sin_precios": "No {comb} prices within {radio} km of home yet.",
        "inicio.sin_precios_nota": "If you just started the app, the first read takes a moment. "
                                   "Otherwise, widen the radius in Settings.",
        "inicio.mas_barata": "Cheapest within {radio} km",
        "inicio.ahorro": "Filling {litros} L here costs <b>{coste}</b>: you save <b>{ahorro}</b> versus the "
                         "local average ({media}).",
        "inicio.resto": "Others near home",
        "inicio.resto_nota": "{total} in total · cents vs. average",
        "como_llegar": "Directions", "historial": "History",
        "actualizar": "Refresh", "actualizar_ahora": "Refresh now",
        "pie.datos": "Prices from Spain's Ministry · data from {fecha}",
        "pie.sin_leer": "Prices from Spain's Ministry · not read yet",

        "mapa.titulo": "Map", "mapa.aria": "Map of petrol stations",
        "mapa.leyenda": '<span class="barata">●</span> cheapest · <span class="cara">●</span> most expensive, '
                        "compared within your radius. Tap one to see its price.",

        "estacion.de_casa": "{distancia} from home",
        "estacion.ultimos": "{comb}, last 90 days",
        "estacion.sin_historico": "No history yet: the app stores one price a day and the chart appears "
                                  "once there are two.",
        "estacion.no_existe": "That station is not in the database.",
        "estacion.coste": "Filling {litros} L of {comb} here: <b>{coste}</b>",
        "serie.esta": "This station", "serie.zona": "Local average", "serie.media": "Average",
        "serie.minimo": "Cheapest", "serie.brent": "Brent (€/barrel)",

        "tend.sin_datos": "No {comb} data for your area yet.",
        "tend.media_hoy": "Average today", "tend.vs7": "Vs. 7 days ago", "tend.vs30": "Vs. 30 days ago",
        "tend.cts": "¢",
        "tend.zona": "{comb} within {radio} km",
        "tend.grafica_pronto": "The chart appears once there are two days of data. The app stores one price a day.",
        "tend.dia_titulo": "Which day is cheapest?",
        "tend.dia_mejor": "On average, <b>{dia}</b> is the cheapest day to fill up around you.",
        "tend.dia_faltan": "At least two weeks of data are needed to tell. You have {dias} days.",

        "prev.titulo": "Fill up today or wait?",
        "prev.brent": "Brent is at {precio} a barrel{cambio}.",
        "prev.brent_cambio": " ({cambio}% in a week)",
        "prev.como": "The forecast looks at how much Brent and your local prices moved over the last week: "
                     "pumps trail oil, and prices have momentum.",
        "prev.prueba": "Tested on the last 60 days without learning from them: it would have been right "
                       "<b>{aciertos} out of {total}</b> times ({pct}%), with an average error of {error} cents.",
        "prev.seguimiento": "Since tracking started: <b>{aciertos} out of {total}</b> right.",
        "prev.apuntando": "Every forecast is logged; in a week you'll start to see whether it really works.",
        "prev.aviso": "It's a hint, not a guarantee: it can't foresee shocks like wars, tax changes or holidays.",
        "prev.cargando": "Loading price history from the Ministry and oil markets. About 100 days of data "
                         "are needed: you have {dias}. The first time takes less than an hour.",
        "sem.llena": "Fill up now", "sem.igual": "No rush", "sem.espera": "Wait if you can",
        "frase.llena": "Expected to rise about {cts} cents this week ({euros} more per tank if you wait).",
        "frase.espera": "Expected to drop about {cts} cents this week ({euros} less per tank if you wait).",
        "frase.igual": "No big changes expected this week.",

        "dia.0": "Monday", "dia.1": "Tuesday", "dia.2": "Wednesday", "dia.3": "Thursday", "dia.4": "Friday",
        "dia.5": "Saturday", "dia.6": "Sunday",
        "dia_frase.0": "Monday", "dia_frase.1": "Tuesday", "dia_frase.2": "Wednesday", "dia_frase.3": "Thursday",
        "dia_frase.4": "Friday", "dia_frase.5": "Saturday", "dia_frase.6": "Sunday",

        "aj.titulo": "Settings", "aj.guardado": "Saved.", "aj.guardar": "Save",
        "aj.prueba_ok": "Test message sent. Check Telegram.",
        "aj.prueba_error": "Couldn't send it. Check TELEGRAM_TOKEN and TELEGRAM_CHAT.",
        "aj.casa": "Home", "aj.buscar_ph": "Street, number and town", "aj.buscar": "Search",
        "aj.buscar_aria": "Search address", "aj.mapa_aria": "Map to place your home",
        "aj.mapa_ayuda": "Search your address, tap the map or drag the pin. Then Save.",
        "aj.mi_ubicacion": "📍 Use my location", "aj.coordenadas": "Enter coordinates",
        "aj.latitud": "Latitude", "aj.longitud": "Longitude", "aj.radio": "Radius (km)",
        "aj.provincias": "Provinces",
        "aj.provincias_nota": "Where prices are read from. It's picked for you when you search your address. "
                              "Choose up to 4, in case you live near a border.",
        "aj.coche": "Car", "aj.combustible": "Fuel", "aj.litros": "Litres per fill-up",
        "aj.avisos": "Telegram alerts",
        "aj.telegram_falta": "Telegram isn't set up: add TELEGRAM_TOKEN and TELEGRAM_CHAT to the container.",
        "aj.resumen": "Morning summary", "aj.hora": "Summary time",
        "aj.chollos": "Alert me about bargains (8:00–22:00)",
        "aj.umbral": "Bargain = below the 30-day average by (€/L)",
        "aj.idioma": "Language", "aj.idioma_auto": "Browser default",
        "aj.enviar_prueba": "Send a test message",
        "aj.version": "Version {version}", "aj.ultima": "last read {fecha}",

        "err.ubicacion": "That location isn't valid.",
        "err.radio": "The radius must be between 1 and 100 km.",
        "err.litros": "Litres per fill-up must be between 1 and 150.",
        "err.umbral": "The bargain threshold is in euros per litre, e.g. 0.05.",
        "err.numero": "One of the numbers isn't written correctly.",
        "err.hora": "Use a time like 08:30.",
        "err.combustible": "That fuel doesn't exist.",
        "err.provincias": "Pick between 1 and 4 provinces.",
        "err.idioma": "That language isn't available.",
        "err.buscador": "The address search isn't responding. Try again in a while.",

        "js.casa": "Home", "js.ver_historial": "See history",
        "js.buscando": "Searching…", "js.escribe_mas": "Type a bit more of the address.",
        "js.no_encontrada": "Couldn't find that address. Try street and town.",
        "js.elige": "Pick the right one:",
        "js.encontrada": "Address found. If it's not your exact door, drag the pin.",
        "js.no_se_pudo_buscar": "Search failed: ", "js.movida": "Pin moved.",
        "js.tocado": "Home set where you tapped.", "js.coordenadas": "Coordinates set.",
        "js.sin_gps": "This browser can't share your location.", "js.buscando_gps": "Finding where you are…",
        "js.gps_ok": "Set to your current location.", "js.no_se_pudo": "Couldn't: ",
        "js.guardar": " Now tap Save.", "js.provincia": " Province: {p}.",

        "off.titulo": "Offline",
        "off.texto": "You're offline and this screen wasn't saved. Open it once while online and it'll "
                     "be available.",
        "off.aviso": "Offline · data from {fecha}",
        "manifest.descripcion": "The cheapest petrol stations near home, and whether to fill up today.",

        "tg.hoy": "⛽ <b>{comb} today</b> within {radio} km",
        "tg.media": "Local average: {media}. Filling {litros} L at the first one costs <b>{coste}</b> "
                    "and saves <b>{ahorro}</b>.",
        "tg.sube": "Up {cts} cents from a week ago.",
        "tg.baja": "Down {cts} cents from a week ago.",
        "tg.igual": "Same as a week ago.",
        "tg.chollo": "🔥 <b>Bargain</b>: {comb} at <b>{precio}</b> at {sitio}.\n"
                     "That's {cts} cents below the 30-day average ({media}).",
        "tg.prueba": "✅ Test from Pumpcast: alerts are working.",
    },
}

# Los textos que necesita el JavaScript de las páginas.
CLAVES_JS = [c for c in TEXTOS["es"] if c.startswith("js.")]


def t(lang: str, clave: str, **huecos) -> str:
    texto = TEXTOS.get(lang, TEXTOS["es"]).get(clave) or TEXTOS["es"][clave]
    return texto.format(**huecos) if huecos else texto


def del_navegador(accept_language: str | None) -> str:
    """El primer idioma que tengamos de la cabecera Accept-Language; si ninguno, inglés."""
    for parte in (accept_language or "").split(","):
        codigo = parte.split(";")[0].strip().lower()[:2]
        if codigo in IDIOMAS:
            return codigo
    return "en"


def elegir(ajuste: str, accept_language: str | None) -> str:
    return ajuste if ajuste in IDIOMAS else del_navegador(accept_language)


def para_js(lang: str) -> dict:
    return {"lang": lang, "decimal": "," if lang == "es" else ".",
            "t": {c[3:]: t(lang, c) for c in CLAVES_JS}}

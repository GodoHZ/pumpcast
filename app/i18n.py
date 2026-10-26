"""Textos en castellano e inglés; los de las otras lenguas de España, en app/idiomas/.

Cada texto tiene una clave; los que llevan {huecos} se rellenan con t(..., hueco=valor).
Los que llevan HTML (<b>) se pintan con |safe en las plantillas, y solo reciben números
ya formateados, nunca texto que venga de fuera.
"""
from __future__ import annotations

# En el orden en que salen en Ajustes, con el nombre de cada una en su lengua.
NOMBRES = {"es": "Español", "ca": "Català", "gl": "Galego", "eu": "Euskara", "oc": "Aranés", "en": "English"}
IDIOMAS = tuple(NOMBRES)

TEXTOS: dict[str, dict[str, str]] = {
    "es": {
        "nav.cerca": "Cerca", "nav.mapa": "Mapa", "nav.tendencia": "Tendencia", "nav.ajustes": "Ajustes",
        "aria.combustible": "Combustible", "aria.secciones": "Secciones",
        "comb.g95": "Gasolina 95", "comb.g98": "Gasolina 98", "comb.diesel": "Diésel",
        "comb.diesel_plus": "Diésel+", "comb.glp": "GLP", "comb.gnc": "GNC", "comb.gnl": "GNL",

        "inicio.primera_vez": "Para empezar, dinos dónde buscar gasolineras: tu casa, el trabajo o donde "
                              "estés ahora. Sirve en toda España.",
        "inicio.ir_ajustes": "Elegir ubicación",
        "inicio.sin_precios": "Aún no hay precios de {comb} a menos de {radio} km.",
        "inicio.sin_precios_nota": "Prueba a ampliar el radio en Ajustes.",
        "inicio.mas_barata": "La más barata a menos de {radio} km",
        "inicio.ahorro": "Llenar {litros} {unidad} aquí te cuesta <b>{coste}</b>: ahorras <b>{ahorro}</b> frente a la "
                         "media de la zona ({media}).",
        "inicio.resto": "El resto cerca",
        "inicio.mas_cercana": "La más cercana", "inicio.ordenar": "Ordenar la lista",
        "orden.precio": "Más baratas", "orden.distancia": "Más cercanas",
        "inicio.resto_nota": "{total} en total · céntimos frente a la media",
        "como_llegar": "Cómo llegar", "historial": "Historial",
        "actualizar_ahora": "Actualizar precios ahora",
        "pie.datos": "Precios del Ministerio · datos de {fecha}",
        "pie.sin_leer": "Precios del Ministerio · sin leer todavía",

        "mapa.titulo": "Mapa", "mapa.aria": "Mapa de gasolineras",
        "mapa.leyenda": '<span class="barata">●</span> más barata · <span class="cara">●</span> más cara, '
                        "comparando las de tu radio. Toca una para ver su precio.",

        "estacion.de_casa": "a {distancia} de tu ubicación",
        "estacion.ultimos": "{comb}, últimos 90 días",
        "estacion.sin_historico": "Todavía no hay histórico: la app guarda un precio al día y la gráfica "
                                  "sale en cuanto haya dos.",
        "estacion.no_existe": "Esa gasolinera no está en la base de datos.",
        "estacion.coste": "Llenar {litros} {unidad} de {comb} aquí: <b>{coste}</b>",
        "serie.esta": "Esta gasolinera", "serie.zona": "Media de la zona", "serie.media": "Media",
        "serie.minimo": "La más barata", "serie.brent": "Brent (€/barril)",

        "tend.sin_datos": "Aún no hay datos de {comb} en tu zona.",
        "tend.media_hoy": "Media hoy", "tend.vs7": "Vs. hace 7 días", "tend.vs30": "Vs. hace 30 días",
        "tend.cts": "cts",
        "tend.zona": "{comb} a menos de {radio} km",
        "tend.grafica_pronto": "La gráfica sale en cuanto haya dos días de datos. La app guarda un precio al día.",
        "tend.dia_titulo": "¿Qué día sale más barato?",
        "tend.dia_mejor": "De media, el <b>{dia}</b> es el día más barato para repostar en tu zona.",
        "tend.brent_retraso": "El Brent llega hasta el {fecha}: la EIA lo publica una vez por semana, con unos días de retraso. La previsión ya lo tiene en cuenta.",
        "js.brent_pendiente": "aún sin publicar",
        "tend.dia_faltan": "Hacen falta al menos dos semanas de datos para saberlo. Llevas {dias} días.",

        "prev.titulo": "¿Lleno hoy o espero?",
        "prev.brent": "El último Brent publicado, del {fecha}, está a {precio} el barril{cambio}.",
        "prev.brent_cambio": " ({cambio} % en una semana)",
        "prev.provincia": "Calculada con los precios de toda la provincia de {provincia}.",
        "prev.como": "La previsión mira cuánto se han movido el Brent y el precio de tu provincia en la "
                     "última semana: el surtidor va detrás del petróleo y los precios tienen inercia.",
        "prev.prueba": "Probado con los últimos 60 días sin usarlos para aprender: habría acertado "
                       "<b>{aciertos} de {total}</b> veces ({pct} %), con un error medio de {error} céntimos.",
        "prev.seguimiento": "Desde que se apuntan: <b>{aciertos} de {total}</b> aciertos.",
        "prev.apuntando": "Se apunta cada previsión; en una semana empezará a verse si acierta de verdad.",
        "prev.aviso": "Es una pista, no una garantía: no prevé sustos como guerras, impuestos o puentes.",
        "prev.cargando": "Cargando el histórico de precios del Ministerio y del petróleo. Hacen falta unos "
                         "100 días de datos: llevas {dias}. La primera vez tarda unas horas.",
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
        "aj.casa": "Ubicación", "aj.buscar_ph": "Calle, número y pueblo", "aj.buscar": "Buscar",
        "aj.buscar_aria": "Buscar dirección", "aj.mapa_aria": "Mapa para elegir la ubicación",
        "aj.privacidad": "Tu ubicación y tus preferencias se guardan solo en este navegador (una cookie). "
                         "El servidor las usa para preparar la página y no las apunta en ningún sitio.",
        "aj.olvidar": "Olvidar mi ubicación",
        "aj.mapa_ayuda": "Busca tu dirección, toca el mapa o arrastra la chincheta. Luego, Guardar.",
        "aj.mi_ubicacion": "Usar mi ubicación", "aj.coordenadas": "Coordenadas a mano",
        "aj.gps": "Usar dónde estoy cada vez que abra la app",
        "aj.gps_nota": "Al abrirla, el móvil dice dónde estás (redondeado a unos 100 m) y busca ahí. "
                       "Si no puede, usa la ubicación de arriba.",
        "aj.latitud": "Latitud", "aj.longitud": "Longitud", "aj.radio": "Radio (km)",
        "aj.coche": "Coche", "aj.combustible": "Combustible", "aj.litros": "Cuánto sueles echar (litros; kilos si es gas natural)",
        "mapas.titulo": "¿Con qué app quieres ir?", "mapas.cancelar": "Cancelar",
        "js.como_llegar": "Cómo llegar",
        "aj.avisos": "Avisos por Telegram",
        "aj.telegram_falta": "Telegram no está configurado: añade TELEGRAM_TOKEN y TELEGRAM_CHAT al contenedor.",
        "aj.resumen": "Resumen cada mañana", "aj.hora": "Hora del resumen",
        "aj.chollos": "Avisarme de chollos (de 8 a 22 h)",
        "aj.umbral": "Chollo = por debajo de la media de 30 días en (€/L)",
        "aj.idioma": "Idioma", "aj.idioma_auto": "El del navegador",
        "aj.enviar_prueba": "Enviar un mensaje de prueba",
        "aj.version": "Versión {version}", "aj.ultima": "última lectura {fecha}",

        "err.ubicacion": "La ubicación no es válida.",
        "err.fuera": "Pumpcast solo tiene precios de España: elige un sitio dentro.",
        "err.radio": "El radio tiene que estar entre 1 y 50 km.",
        "err.litros": "Lo que echas en cada repostaje tiene que estar entre 1 y 150.",
        "err.umbral": "El umbral del chollo va en euros por litro, por ejemplo 0,05.",
        "err.numero": "Hay algún número mal escrito.",
        "err.hora": "La hora del aviso va como 08:30.",
        "err.combustible": "Ese combustible no existe.",
        "err.idioma": "Ese idioma no está disponible.",

        "js.casa": "Tu ubicación", "js.ver_historial": "Ver historial",
        "js.buscando": "Buscando…", "js.escribe_mas": "Escribe un poco más de la dirección.",
        "js.no_encontrada": "No he encontrado esa dirección. Prueba con calle y pueblo.",
        "js.elige": "Elige la buena:",
        "js.encontrada": "Dirección encontrada. Si no es justo tu portal, arrastra la chincheta.",
        "js.no_se_pudo_buscar": "No se pudo buscar: ", "js.movida": "Chincheta movida.",
        "js.tocado": "Ubicación puesta donde has tocado.", "js.coordenadas": "Coordenadas puestas.",
        "js.sin_gps": "Este navegador no da la ubicación.", "js.buscando_gps": "Buscando dónde estás…",
        "js.gps_ok": "Puesta tu ubicación actual.", "js.no_se_pudo": "No se pudo: ",
        "js.guardar": " Dale a Guardar.",
        "js.fuente_busqueda": "(Búsqueda: © OpenStreetMap, Nominatim)",
        "pie.fuente": "Precios: Ministerio para la Transición Ecológica y el Reto Demográfico",
        "legal.en_castellano": "",
        "pie.actualizado": "actualizados {fecha}", "pie.legal": "Aviso legal y privacidad",
        "e404.titulo": "Esta página no existe",
        "e404.texto": "Puede que el enlace esté mal escrito o que la página ya no exista.",
        "e404.volver": "Ir al inicio",
        "js.gps_movido": "Te has movido: buscando gasolineras aquí…",
        "js.gps_ultima": "No sé dónde estás ahora: uso tu última ubicación.",
        "js.gps_fuera": "Ahora estás fuera de España: uso tu última ubicación.",
        "js.falta_ubicacion": "Primero elige dónde: busca una dirección, toca el mapa o usa tu ubicación.",

        "off.titulo": "Sin conexión",
        "off.texto": "No hay conexión y esta pantalla no estaba guardada. Ábrela una vez con conexión "
                     "y quedará disponible.",
        "off.aviso": "Sin conexión · datos del {fecha}",
        "manifest.descripcion": "Las gasolineras más baratas cerca de ti y si sale a cuenta llenar hoy.",
        "api.sin_ubicacion": "Falta la ubicación: añade ?lat=...&lon=... a la URL o elígela en Ajustes.",

        "admin.titulo": "Administración", "admin.entrar": "Entrar", "admin.salir": "Salir",
        "admin.clave": "Contraseña", "admin.codigo": "Código de 6 cifras de tu app de autenticación",
        "admin.error": "Contraseña o código incorrectos.",
        "admin.bloqueado": "Demasiados intentos fallidos. Espera un cuarto de hora.",
        "admin.alta_titulo": "Verificación en dos pasos",
        "admin.alta_texto": "Para terminar de proteger el panel, añádelo a tu app de autenticación (Google "
                            "Authenticator, Aegis, 1Password...): escanea el código, o pulsa el botón si estás "
                            "en el móvil. Después escribe el código de 6 cifras que te dé.",
        "admin.alta_qr": "Código QR para la app de autenticación",
        "admin.alta_enlace": "Abrir en la app de autenticación",
        "admin.alta_clave": "O escribe esta clave a mano en la app:",
        "admin.confirmar": "Confirmar y entrar",
        "admin.codigo_mal": "Ese código no vale. Comprueba que la hora del móvil está bien y prueba con el siguiente.",
        "admin.ubicacion": "Ubicación de los avisos",
        "admin.ubicacion_nota": "Solo para tus avisos de Telegram. No se muestra en la web.",
        "admin.idioma_avisos": "Idioma de los avisos",
        "admin.lectura_ok": "Precios actualizados.",
        "admin.lectura_error": "No se pudieron leer los precios del Ministerio. Se reintentará solo.",

        "tg.hoy": "⛽ <b>{comb} hoy</b> a menos de {radio} km",
        "tg.media": "Media de la zona: {media}. Llenar {litros} {unidad} en la primera cuesta <b>{coste}</b> "
                    "y ahorras <b>{ahorro}</b>.",
        "tg.sube": "Sube {cts} céntimos desde hace una semana.",
        "tg.baja": "Baja {cts} céntimos desde hace una semana.",
        "tg.igual": "Igual que hace una semana.",
        "tg.chollo": "🔥 <b>Chollo</b>: {comb} a <b>{precio}</b> en {sitio}.\n"
                     "Son {cts} céntimos menos que la media de los últimos 30 días ({media}).",
        "tg.prueba": "✅ Prueba desde Pumpcast: los avisos llegan bien.",
        "inicio.mas_barata_abierta": "La más barata abierta a menos de {radio} km",
        "inicio.favoritas": "Tus favoritas",
        "orden.compensa": "Más rentables",
        "inicio.con_viaje": "{coste} con el viaje",
        "inicio.compensa_nota": "A la derecha, lo que pagas por {litros} {unidad} más el combustible de ir y volver, con un consumo de {consumo} {unidad}/100 km. Cámbialo en Ajustes.",
        "hor.24h": "Abierta 24 h",
        "hor.cierra": "Abierta · cierra a las {hora}",
        "hor.abre": "Cerrada · abre a las {hora}",
        "hor.cerrada": "Cerrada ahora",
        "hor.publicado": "Horario publicado: {horario}. Los festivos pueden cambiarlo.",
        "fav.poner": "Favorita",
        "fav.quitar": "Quitar de favoritas",
        "compartir": "Compartir",
        "js.guardado": "Guardado",
        "js.copiado": "Enlace copiado",
        "js.cerrada": "cerrada ahora",
        "aj.consumo": "Consumo del coche (litros o kilos a los 100 km)",
        "err.consumo": "El consumo tiene que estar entre 1 y 40.",
        "admin.brent_viejo": "El Brent no se actualiza desde el {fecha}: la previsión puede fallar. Mira el registro del contenedor.",
        "aj.apariencia": "Idioma y aspecto",
        "aj.tema": "Tema",
        "tema.auto": "El del móvil",
        "tema.claro": "Claro",
        "tema.oscuro": "Oscuro",
        "inicio.mas_cercana_abierta": "La más cercana abierta",
        "inicio.mas_rentable": "La más rentable a menos de {radio} km",
        "inicio.mas_rentable_abierta": "La más rentable abierta a menos de {radio} km",
        "inicio.rentable_viaje": "Contando el viaje de ida y vuelta: {coste}",
        "inst.titulo": "Tenla como una app",
        "inst.texto": "Se abre a pantalla completa desde tu pantalla de inicio. No ocupa casi nada.",
        "inst.ios_1": "Pulsa {icono} <b>Compartir</b> en la barra de Safari.",
        "inst.ios_2": "Elige {icono} <b>Añadir a pantalla de inicio</b>.",
        "inst.ios_3": "Pulsa <b>Añadir</b>.",
        "inst.otra_app": "Desde aquí no se puede instalar: ábrela en Safari o en Chrome.",
        "inst.instalar": "Instalar",
        "inst.cerrar": "Ahora no",
        "aj.instalar": "Instalar la app",
        "inst.otro_1": "Abre el menú {icono} del navegador.",
        "inst.otro_2": "Elige <b>Instalar app</b> o <b>Añadir a pantalla de inicio</b>.",
        "aj.instalada": "Ya tienes Pumpcast instalada como app.",
    },
    "en": {
        "nav.cerca": "Nearby", "nav.mapa": "Map", "nav.tendencia": "Trends", "nav.ajustes": "Settings",
        "aria.combustible": "Fuel", "aria.secciones": "Sections",
        "comb.g95": "Petrol 95", "comb.g98": "Petrol 98", "comb.diesel": "Diesel",
        "comb.diesel_plus": "Diesel+", "comb.glp": "LPG", "comb.gnc": "CNG", "comb.gnl": "LNG",

        "inicio.primera_vez": "To get started, tell us where to look for petrol stations: home, work or "
                              "wherever you are now. It works anywhere in Spain.",
        "inicio.ir_ajustes": "Choose location",
        "inicio.sin_precios": "No {comb} prices within {radio} km yet.",
        "inicio.sin_precios_nota": "Try widening the radius in Settings.",
        "inicio.mas_barata": "Cheapest within {radio} km",
        "inicio.ahorro": "Filling {litros} {unidad} here costs <b>{coste}</b>: you save <b>{ahorro}</b> versus the "
                         "local average ({media}).",
        "inicio.resto": "Others nearby",
        "inicio.mas_cercana": "Nearest", "inicio.ordenar": "Sort the list",
        "orden.precio": "Cheapest", "orden.distancia": "Nearest",
        "inicio.resto_nota": "{total} in total · cents vs. average",
        "como_llegar": "Directions", "historial": "History",
        "actualizar_ahora": "Refresh prices now",
        "pie.datos": "Prices from Spain's Ministry · data from {fecha}",
        "pie.sin_leer": "Prices from Spain's Ministry · not read yet",

        "mapa.titulo": "Map", "mapa.aria": "Map of petrol stations",
        "mapa.leyenda": '<span class="barata">●</span> cheapest · <span class="cara">●</span> most expensive, '
                        "compared within your radius. Tap one to see its price.",

        "estacion.de_casa": "{distancia} from your location",
        "estacion.ultimos": "{comb}, last 90 days",
        "estacion.sin_historico": "No history yet: the app stores one price a day and the chart appears "
                                  "once there are two.",
        "estacion.no_existe": "That station is not in the database.",
        "estacion.coste": "Filling {litros} {unidad} of {comb} here: <b>{coste}</b>",
        "serie.esta": "This station", "serie.zona": "Local average", "serie.media": "Average",
        "serie.minimo": "Cheapest", "serie.brent": "Brent (€/barrel)",

        "tend.sin_datos": "No {comb} data for your area yet.",
        "tend.media_hoy": "Average today", "tend.vs7": "Vs. 7 days ago", "tend.vs30": "Vs. 30 days ago",
        "tend.cts": "¢",
        "tend.zona": "{comb} within {radio} km",
        "tend.grafica_pronto": "The chart appears once there are two days of data. The app stores one price a day.",
        "tend.dia_titulo": "Which day is cheapest?",
        "tend.dia_mejor": "On average, <b>{dia}</b> is the cheapest day to fill up around you.",
        "tend.brent_retraso": "Brent runs until {fecha}: the EIA publishes it once a week, a few days late. The forecast already allows for that.",
        "js.brent_pendiente": "not published yet",
        "tend.dia_faltan": "At least two weeks of data are needed to tell. You have {dias} days.",

        "prev.titulo": "Fill up today or wait?",
        "prev.brent": "The latest published Brent, from {fecha}, is {precio} a barrel{cambio}.",
        "prev.brent_cambio": " ({cambio}% in a week)",
        "prev.provincia": "Based on prices across the province of {provincia}.",
        "prev.como": "The forecast looks at how much Brent and prices in your province moved over the last "
                     "week: pumps trail oil, and prices have momentum.",
        "prev.prueba": "Tested on the last 60 days without learning from them: it would have been right "
                       "<b>{aciertos} out of {total}</b> times ({pct}%), with an average error of {error} cents.",
        "prev.seguimiento": "Since tracking started: <b>{aciertos} out of {total}</b> right.",
        "prev.apuntando": "Every forecast is logged; in a week you'll start to see whether it really works.",
        "prev.aviso": "It's a hint, not a guarantee: it can't foresee shocks like wars, tax changes or holidays.",
        "prev.cargando": "Loading price history from the Ministry and oil markets. About 100 days of data "
                         "are needed: you have {dias}. The first time takes a few hours.",
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
        "aj.casa": "Location", "aj.buscar_ph": "Street, number and town", "aj.buscar": "Search",
        "aj.buscar_aria": "Search address", "aj.mapa_aria": "Map to choose the location",
        "aj.privacidad": "Your location and preferences are stored only in this browser (a cookie). The "
                         "server uses them to build the page and doesn't record them anywhere.",
        "aj.olvidar": "Forget my location",
        "aj.mapa_ayuda": "Search your address, tap the map or drag the pin. Then Save.",
        "aj.mi_ubicacion": "Use my location", "aj.coordenadas": "Enter coordinates",
        "aj.gps": "Use where I am every time I open the app",
        "aj.gps_nota": "When you open it, your phone shares where you are (rounded to about 100 m) and "
                       "searches there. If it can't, it uses the location above.",
        "aj.latitud": "Latitude", "aj.longitud": "Longitude", "aj.radio": "Radius (km)",
        "aj.coche": "Car", "aj.combustible": "Fuel", "aj.litros": "Usual fill-up (litres; kilos for natural gas)",
        "mapas.titulo": "Which app do you want to use?", "mapas.cancelar": "Cancel",
        "js.como_llegar": "Directions",
        "aj.avisos": "Telegram alerts",
        "aj.telegram_falta": "Telegram isn't set up: add TELEGRAM_TOKEN and TELEGRAM_CHAT to the container.",
        "aj.resumen": "Morning summary", "aj.hora": "Summary time",
        "aj.chollos": "Alert me about bargains (8:00–22:00)",
        "aj.umbral": "Bargain = below the 30-day average by (€/L)",
        "aj.idioma": "Language", "aj.idioma_auto": "Browser default",
        "aj.enviar_prueba": "Send a test message",
        "aj.version": "Version {version}", "aj.ultima": "last read {fecha}",

        "err.ubicacion": "That location isn't valid.",
        "err.fuera": "Pumpcast only has prices for Spain: pick a place there.",
        "err.radio": "The radius must be between 1 and 50 km.",
        "err.litros": "Your usual fill-up must be between 1 and 150.",
        "err.umbral": "The bargain threshold is in euros per litre, e.g. 0.05.",
        "err.numero": "One of the numbers isn't written correctly.",
        "err.hora": "Use a time like 08:30.",
        "err.combustible": "That fuel doesn't exist.",
        "err.idioma": "That language isn't available.",

        "js.casa": "Your location", "js.ver_historial": "See history",
        "js.buscando": "Searching…", "js.escribe_mas": "Type a bit more of the address.",
        "js.no_encontrada": "Couldn't find that address. Try street and town.",
        "js.elige": "Pick the right one:",
        "js.encontrada": "Address found. If it's not your exact door, drag the pin.",
        "js.no_se_pudo_buscar": "Search failed: ", "js.movida": "Pin moved.",
        "js.tocado": "Location set where you tapped.", "js.coordenadas": "Coordinates set.",
        "js.sin_gps": "This browser can't share your location.", "js.buscando_gps": "Finding where you are…",
        "js.gps_ok": "Set to your current location.", "js.no_se_pudo": "Couldn't: ",
        "js.guardar": " Now tap Save.",
        "js.fuente_busqueda": "(Search: © OpenStreetMap, Nominatim)",
        "pie.fuente": "Prices: Spanish Ministry for the Ecological Transition",
        "legal.en_castellano": "",
        "pie.actualizado": "updated {fecha}", "pie.legal": "Legal notice and privacy",
        "e404.titulo": "This page doesn't exist",
        "e404.texto": "The link may be mistyped, or the page may no longer exist.",
        "e404.volver": "Go to the home page",
        "js.gps_movido": "You've moved: finding stations here…",
        "js.gps_ultima": "Can't tell where you are right now: using your last location.",
        "js.gps_fuera": "You're outside Spain right now: using your last location.",
        "js.falta_ubicacion": "First choose where: search an address, tap the map or use your location.",

        "off.titulo": "Offline",
        "off.texto": "You're offline and this screen wasn't saved. Open it once while online and it'll "
                     "be available.",
        "off.aviso": "Offline · data from {fecha}",
        "manifest.descripcion": "The cheapest petrol stations near you, and whether to fill up today.",
        "api.sin_ubicacion": "Location missing: add ?lat=...&lon=... to the URL or choose it in Settings.",

        "admin.titulo": "Admin", "admin.entrar": "Sign in", "admin.salir": "Sign out",
        "admin.clave": "Password", "admin.codigo": "6-digit code from your authenticator app",
        "admin.error": "Wrong password or code.",
        "admin.bloqueado": "Too many failed attempts. Wait fifteen minutes.",
        "admin.alta_titulo": "Two-step verification",
        "admin.alta_texto": "To finish protecting the panel, add it to your authenticator app (Google "
                            "Authenticator, Aegis, 1Password...): scan the code, or tap the button if you're on "
                            "your phone. Then type the 6-digit code it shows.",
        "admin.alta_qr": "QR code for the authenticator app",
        "admin.alta_enlace": "Open in authenticator app",
        "admin.alta_clave": "Or type this key into the app by hand:",
        "admin.confirmar": "Confirm and sign in",
        "admin.codigo_mal": "That code isn't valid. Check your phone's clock and try the next one.",
        "admin.ubicacion": "Alert location",
        "admin.ubicacion_nota": "Only for your Telegram alerts. It's never shown on the website.",
        "admin.idioma_avisos": "Alert language",
        "admin.lectura_ok": "Prices updated.",
        "admin.lectura_error": "Couldn't read prices from the Ministry. It will retry on its own.",

        "tg.hoy": "⛽ <b>{comb} today</b> within {radio} km",
        "tg.media": "Local average: {media}. Filling {litros} {unidad} at the first one costs <b>{coste}</b> "
                    "and saves <b>{ahorro}</b>.",
        "tg.sube": "Up {cts} cents from a week ago.",
        "tg.baja": "Down {cts} cents from a week ago.",
        "tg.igual": "Same as a week ago.",
        "tg.chollo": "🔥 <b>Bargain</b>: {comb} at <b>{precio}</b> at {sitio}.\n"
                     "That's {cts} cents below the 30-day average ({media}).",
        "tg.prueba": "✅ Test from Pumpcast: alerts are working.",
        "inicio.mas_barata_abierta": "Cheapest open within {radio} km",
        "inicio.favoritas": "Your favourites",
        "orden.compensa": "Best value",
        "inicio.con_viaje": "{coste} with the trip",
        "inicio.compensa_nota": "On the right, what you pay for {litros} {unidad} plus the fuel to get there and back, at {consumo} {unidad}/100 km. Change it in Settings.",
        "hor.24h": "Open 24 h",
        "hor.cierra": "Open · closes at {hora}",
        "hor.abre": "Closed · opens at {hora}",
        "hor.cerrada": "Closed now",
        "hor.publicado": "Published hours: {horario}. Holidays may differ.",
        "fav.poner": "Favourite",
        "fav.quitar": "Remove from favourites",
        "compartir": "Share",
        "js.guardado": "Saved",
        "js.copiado": "Link copied",
        "js.cerrada": "closed now",
        "aj.consumo": "Car consumption (litres or kilos per 100 km)",
        "err.consumo": "Consumption must be between 1 and 40.",
        "admin.brent_viejo": "Brent hasn't updated since {fecha}: the forecast may be off. Check the container log.",
        "aj.apariencia": "Language and look",
        "aj.tema": "Theme",
        "tema.auto": "Device default",
        "tema.claro": "Light",
        "tema.oscuro": "Dark",
        "inicio.mas_cercana_abierta": "Nearest open",
        "inicio.mas_rentable": "Best value within {radio} km",
        "inicio.mas_rentable_abierta": "Best value open within {radio} km",
        "inicio.rentable_viaje": "Including the round trip: {coste}",
        "inst.titulo": "Get it as an app",
        "inst.texto": "It opens full screen from your home screen and takes up almost no space.",
        "inst.ios_1": "Tap {icono} <b>Share</b> in Safari's toolbar.",
        "inst.ios_2": "Choose {icono} <b>Add to Home Screen</b>.",
        "inst.ios_3": "Tap <b>Add</b>.",
        "inst.otra_app": "It can't be installed from here: open it in Safari or Chrome.",
        "inst.instalar": "Install",
        "inst.cerrar": "Not now",
        "aj.instalar": "Install the app",
        "inst.otro_1": "Open the browser menu {icono}.",
        "inst.otro_2": "Choose <b>Install app</b> or <b>Add to Home screen</b>.",
        "aj.instalada": "Pumpcast is already installed as an app.",
    },
}

from .idiomas import ca, eu, gl, oc  # noqa: E402

TEXTOS.update(ca=ca.TEXTOS, gl=gl.TEXTOS, eu=eu.TEXTOS, oc=oc.TEXTOS)

# Los textos que necesita el JavaScript de las páginas.
CLAVES_JS = [c for c in TEXTOS["es"] if c.startswith("js.")]


def t(lang: str, clave: str, **huecos) -> str:
    texto = TEXTOS.get(lang, TEXTOS["es"]).get(clave) or TEXTOS["es"][clave]
    return texto.format(**huecos) if huecos else texto


def del_navegador(accept_language: str | None) -> str:
    """El primer idioma que tengamos de la cabecera Accept-Language; si ninguno, inglés. Sin
    cabecera (los robots que leen el enlace al compartirlo en WhatsApp, Telegram...), castellano."""
    if not accept_language:
        return "es"
    for parte in accept_language.split(","):
        codigo = parte.split(";")[0].strip().lower()[:2]
        if codigo in IDIOMAS:
            return codigo
    return "en"


def elegir(ajuste: str, accept_language: str | None) -> str:
    return ajuste if ajuste in IDIOMAS else del_navegador(accept_language)


def europeo(lang: str) -> bool:
    """Coma decimal, el euro detrás y el día antes que el mes: todas menos el inglés."""
    return lang != "en"


def para_js(lang: str) -> dict:
    return {"lang": lang, "decimal": "," if europeo(lang) else ".", "europeo": europeo(lang),
            "t": {c[3:]: t(lang, c) for c in CLAVES_JS}}

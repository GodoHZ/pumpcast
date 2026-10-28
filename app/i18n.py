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
        "filtro.aria": "Filtrar el mapa",
        "filtro.abiertas": "Abiertas ahora",
        "filtro.baratas": "Más baratas", "filtro.baratas_ayuda": "Más baratas que la media",
        "filtro.marcas": "Marcas",
        "filtro.marcas_titulo": "¿Qué marcas quieres ver?",
        "filtro.todas": "Todas",
        "filtro.ninguna": "Ninguna",
        "filtro.listo": "Listo",
        "js.filtro_cuenta": "{n} de {total} gasolineras.",
        "mapa.leyenda": '<span class="barata" aria-hidden="true">●</span> más barata · <span class="cara" aria-hidden="true">●</span> más cara, '
                        "comparando las de tu radio. Toca una para ver su horario y cómo llegar.",
        "mapa.cerrar": "Cerrar",

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
        "marcas.titulo": "Marcas en tu zona",
        "marcas.nota": "Cuánto más barata o más cara que la media sale cada marca, de media en los últimos "
                       "{dias} días y a menos de {radio} km. Solo marcas con al menos dos gasolineras.",
        "marcas.gasolineras": "{n} gasolineras",
        "rep.titulo": "Mis repostajes",
        "rep.aqui": "Apuntar repostaje",
        "rep.este_mes": "Este mes",
        "rep.doce_meses": "Últimos 12 meses",
        "rep.consumo": "Consumo ({unidad}/100 km)",
        "rep.consumo_falta": "Para saber tu consumo real, apunta los km del cuentakilómetros en dos "
                             "repostajes de depósito lleno.",
        "rep.usar_consumo": "Usar mi consumo real en Ajustes",
        "rep.consumo_valor": "{consumo} {unidad}/100 km",
        "rep.apuntar": "Apuntar un repostaje",
        "rep.fecha": "Fecha",
        "rep.litros": "Cantidad ({unidad})",
        "rep.precio": "Precio (€/{unidad})",
        "rep.km": "Cuentakilómetros (km, opcional)",
        "rep.lleno": "He llenado el depósito",
        "rep.guardar": "Guardar repostaje",
        "rep.privado": "Se guarda solo en este navegador: Pumpcast no lo ve. Si cambias de móvil o borras los "
                       "datos del navegador, se pierde; exporta una copia de vez en cuando.",
        "rep.historial": "Historial",
        "rep.vacio": "Aún no has apuntado ningún repostaje.",
        "rep.ahorro_titulo": "Lo que llevas ahorrado",
        "rep.ahorro_bien": "ahorrados frente a la media de tu zona (12 meses)",
        "rep.ahorro_mal": "pagados de más frente a la media de tu zona (12 meses)",
        "rep.ahorro_nota": "Compara lo que pagaste en {n} repostajes con la media de {comb} de ese día en tu "
                           "zona.",
        "rep.ahorro_sin": "Cuando apuntes repostajes, aquí verás cuánto ahorras frente a la media de tu zona.",
        "rep.frente_media": "{dif} cts/{unidad} frente a la media",
        "fav.novedades": "Tus favoritas hoy",
        "fav.bajado": "<b>{nombre}</b> ha bajado {cts} cts {cuando}",
        "fav.subido": "<b>{nombre}</b> ha subido {cts} cts {cuando}",
        "fav.ayer": "desde ayer",
        "fav.dias": "en {n} días",
        "coche.titulo": "Modo coche",
        "coche.salir": "Salir del modo coche",
        "coche.ir": "Ir",
        "coche.buscando": "Buscando dónde estás…",
        "coche.desde_ajustes": "Desde tu ubicación de Ajustes",
        "coche.aqui": "Desde donde estás",
        "coche.otras": "Otras cerca",
        "coche.nada": "No hay gasolineras con {comb} a menos de {radio} km.",
        "coche.pantalla": "La pantalla se queda encendida mientras está abierto.",
        "coche.actualizar": "Actualizar",
        "bien.titulo": "Te damos la bienvenida",
        "bien.texto": "Tres toques y listo. Lo que elijas se guarda solo en este navegador.",
        "bien.paso": "Paso {n} de 3",
        "bien.donde": "¿Dónde buscamos?",
        "bien.gps": "Usar dónde estoy",
        "bien.o": "o escribe una dirección",
        "bien.que": "¿Qué echas?",
        "bien.radio": "¿Hasta dónde irías?",
        "bien.km": "{n} km",
        "bien.empezar": "Empezar",
        "bien.atras": "Atrás",
        "bien.lista": "Ubicación lista ✓",
        "bien.sin_js": "Para elegir dónde buscar, ve a Ajustes.",
        "rep.exportar": "Exportar copia",
        "rep.importar": "Importar copia",
        "rep.error": "Revisa la cantidad y el precio (y los km, si los pones).",
        "rep.borrar": "Borrar",
        "rep.borrar_seguro": "¿Borrar este repostaje?",
        "rep.importados": "Importados {n} repostajes.",
        "rep.importar_mal": "Ese archivo no es una copia de Pumpcast.",
        "rep.lleno_corto": "lleno",
        "rep.km_corto": "{km} km",
        "voz.titulo": "Con Siri o el asistente",
        "voz.intro": "Pide la gasolinera sin tocar el móvil: dices <b>«Oye Siri, gasolinera barata»</b> y se "
                     "abre la app de mapas camino de la más barata de alrededor que esté abierta. Pensado "
                     "para el coche.",
        "voz.ajustes": "Busca en tu radio de Ajustes ({radio} km) y con tu combustible ({comb}).",
        "voz.iphone": "iPhone y CarPlay: con Siri",
        "voz.instalar": "Instalar el atajo",
        "voz.atajo_viene": "Viene preparado para {comb} y {app}.",
        "voz.atajo_cambiar": "Para lo tuyo, después de instalarlo edita la dirección del atajo y cambia "
                             "<code>{de}</code> por <code>{a}</code>.",
        "voz.o_crealo": "O créalo tú en un par de minutos:",
        "voz.paso1": "Abre la app <b>Atajos</b> y toca <b>+</b> para crear uno nuevo.",
        "voz.paso2": "Añade <b>Obtener ubicación actual</b>.",
        "voz.b2": "Añade <b>Obtener contenido de URL</b> y pega esta dirección (tócala para copiarla):",
        "voz.b2_nota": "Cambia LAT por tu posición: bórralo, toca «Ubicación actual» encima del teclado, toca "
                       "esa variable y elige <b>Latitud</b>. Igual con LON y <b>Longitud</b>.",
        "voz.b3": "Añade <b>Abrir URL</b>: abrirá lo que ha devuelto el paso anterior, que es la ruta en tu "
                  "app de mapas.",
        "voz.permiso": "Apple Maps enseña la ruta y hay que tocar «Ir»; Google Maps y Waze arrancan solos. "
                       "Con el móvil bloqueado, iOS puede pedirte desbloquearlo.",
        "voz.simple_titulo": "Versión de una sola acción",
        "voz.simple": "Más fácil de crear: solo <b>Abrir URL</b> con esta dirección. Pero se abre Safari, que "
                      "te pide la ubicación (Ajustes › Apps › Safari › Ubicación › Permitir, para que no "
                      "pregunte más) y, antes de abrir el mapa, iOS pregunta «¿Abrir esta página en…?»: hay "
                      "que tocar «Abrir».",
        "voz.paso3": "Ponle de nombre <b>Gasolinera barata</b> (o lo que quieras decir) y guárdalo. Ya está: "
                     "«Oye Siri, gasolinera barata».",
        "voz.otros": "Para otra app de mapas, añade al final <code>&amp;mapa=google</code>, "
                     "<code>&amp;mapa=waze</code> o <code>&amp;mapa=apple</code>. Para la más cercana en vez "
                     "de la más barata, <code>&amp;orden=distancia</code>; para la que más compensa contando "
                     "el viaje, <code>&amp;orden=compensa</code>.",
        "voz.avanzado_titulo": "Que Siri te diga el precio en voz alta",
        "voz.avanzado": "Con unas acciones más, Siri contesta («La más barata a menos de 10 km es Ballenoil, "
                        "a 1,4 km: 1,729 euros el litro») y luego abre el mapa. Así tampoco hace falta el "
                        "permiso de Safari:",
        "voz.a1": "Añade <b>Obtener ubicación actual</b>.",
        "voz.a2": "Añade <b>Obtener contenido de URL</b> con esta dirección, cambiando LAT y LON por las "
                  "variables <b>Latitud</b> y <b>Longitud</b> de la ubicación:",
        "voz.a3": "Añade <b>Obtener valor de diccionario</b> (busca «diccionario») con la clave <b>frase</b> "
                  "y, después, la acción que lee un texto en voz alta (busca «texto»).",
        "voz.a4": "Añade otra vez <b>Obtener valor de diccionario</b>, con la clave <b>apple</b> (o "
                  "<b>google</b>, <b>waze</b>) y, como diccionario, el <b>Contenido de la URL</b>. Termina "
                  "con <b>Abrir URL</b>.",
        "voz.android": "Android: a un toque",
        "voz.android_texto": "Google no deja que una web añada órdenes de voz a su asistente. Lo más cómodo: "
                             "instala Pumpcast en la pantalla de inicio, mantén pulsado su icono y elige "
                             "<b>Más barata cerca</b>; puedes arrastrar ese acceso a la pantalla para tenerlo "
                             "a un toque. Abre Google Maps ya navegando hacia ella.",
        "voz.probar": "Probar ahora",
        "voz.atajo": "Más barata cerca",
        "voz.buscando": "Buscando dónde estás…",
        "voz.abrir_app": "Abrir Pumpcast",
        "pasar.titulo": "Pasar a otro móvil",
        "pasar.intro": "Lleva tus ajustes, tus favoritas y tus repostajes a otro móvil o navegador, sin "
                       "cuentas: escanea el código con la cámara del otro móvil o mándate el enlace.",
        "pasar.lleva": "Lleva {que}.",
        "pasar.ajustes": "tus ajustes y tu ubicación",
        "pasar.favoritas": "{n} favoritas",
        "pasar.repostajes": "{n} repostajes",
        "pasar.y": "y ",
        "pasar.nada": "Aún no hay nada que pasar: elige tu ubicación en Ajustes.",
        "pasar.qr_aria": "Código QR con el enlace para pasar tus datos",
        "pasar.grande": "Hay demasiados datos para un código QR: usa el enlace.",
        "pasar.compartir": "Compartir el enlace",
        "pasar.copiar": "Copiar el enlace",
        "pasar.privado": "Todo va dentro del enlace, detrás del «#»: esa parte nunca llega al servidor. Quien "
                         "tenga el enlace ve tu ubicación, así que mándatelo solo a ti.",
        "pasar.importar_titulo": "Traer desde otro móvil",
        "pasar.importar_intro": "Este enlace trae",
        "pasar.importar_aviso": "Sustituye los ajustes y las favoritas de este móvil; los repostajes se suman "
                                "a los que haya.",
        "pasar.importar_boton": "Importar en este móvil",
        "pasar.importado": "Hecho: ya lo tienes todo en este móvil.",
        "pasar.importar_mal": "Este enlace está incompleto o no es de Pumpcast.",
        "pasar.ir_inicio": "Ir a Pumpcast",
        "voz.precio": "La más barata a menos de {radio} km es {nombre}, en {municipio}, a {distancia}: "
                      "{precio} euros el {unidad}.",
        "voz.distancia": "La más cercana es {nombre}, en {municipio}, a {distancia}: {precio} euros el "
                         "{unidad}.",
        "voz.compensa": "La que más te compensa a menos de {radio} km es {nombre}, en {municipio}, a "
                        "{distancia}: {precio} euros el {unidad}.",
        "voz.nada": "No encuentro gasolineras con precio a menos de {radio} km.",
        "voz.fuera": "Esa ubicación está fuera de España, y Pumpcast solo tiene las gasolineras de España.",
        "voz.unidad_l": "litro",
        "voz.unidad_kg": "kilo",
        "voz.hor_24h": "Está abierta las 24 horas.",
        "voz.hor_cierra": "Cierra a las {hora}.",
        "voz.hor_abre": "Ahora está cerrada; abre a las {hora}.",
        "voz.hor_cerrada": "Ahora está cerrada.",

        "prev.titulo": "¿Lleno hoy o espero?",
        "prev.provincia": "Calculada con los precios de toda la provincia de {provincia}.",
        "prev.nombre_gasoil": "Gasóleo mayorista", "prev.nombre_gasolina": "Gasolina mayorista",
        "prev.semana_hasta": "semana hasta el {fecha}",
        "prev.acierta": "Acierta el {pct} % de las veces; decir siempre «Da igual», el {base} %.",
        "prev.detalles": "¿Cómo se calcula?",
        "prev.como": "La previsión mira cuánto ha subido o bajado el combustible al por mayor (el Brent, para "
                     "los gases) en la última semana publicada y cuánto se ha movido el precio de tu "
                     "provincia: el surtidor va detrás del mercado, sube antes de lo que baja y los precios "
                     "tienen inercia.",
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
        "aj.mapa": "App de mapas para ir",
        "aj.mapa_preguntar": "Preguntar cada vez",
        "aj.mapa_google": "Google Maps",
        "aj.mapa_apple": "Apple Maps",
        "aj.mapa_waze": "Waze",
        "voz.elegir_una_vez": "Para no tener que elegir, pon tu app en <a href=\"/ajustes\">Ajustes</a> y "
                              "vuelve a copiar la dirección del atajo en <a href=\"/voz\">Con Siri</a>.",
        "voz.con_app": "La dirección ya abre <b>{app}</b>, la app de mapas de tus Ajustes. Si la cambias, "
                       "vuelve a copiarla.",
        "voz.sin_app": "Así te preguntará cada vez con qué app ir. Para que vaya directa, elige tu app de "
                       "mapas en <a href=\"/ajustes\">Ajustes</a> y vuelve aquí a copiar la dirección.",
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
        "filtro.aria": "Filter the map",
        "filtro.abiertas": "Open now",
        "filtro.baratas": "Cheaper", "filtro.baratas_ayuda": "Cheaper than average",
        "filtro.marcas": "Brands",
        "filtro.marcas_titulo": "Which brands do you want to see?",
        "filtro.todas": "All",
        "filtro.ninguna": "None",
        "filtro.listo": "Done",
        "js.filtro_cuenta": "{n} of {total} stations.",
        "mapa.leyenda": '<span class="barata" aria-hidden="true">●</span> cheapest · <span class="cara" aria-hidden="true">●</span> most expensive, '
                        "compared within your radius. Tap one for its hours and directions.",
        "mapa.cerrar": "Close",

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
        "marcas.titulo": "Brands near you",
        "marcas.nota": "How much cheaper or dearer than the local average each brand is, on average over the "
                       "last {dias} days within {radio} km. Only brands with at least two stations.",
        "marcas.gasolineras": "{n} stations",
        "rep.titulo": "My fill-ups",
        "rep.aqui": "Log a fill-up",
        "rep.este_mes": "This month",
        "rep.doce_meses": "Last 12 months",
        "rep.consumo": "Use ({unidad}/100 km)",
        "rep.consumo_falta": "To get your real fuel use, enter the odometer reading on two full-tank "
                             "fill-ups.",
        "rep.usar_consumo": "Use my real fuel use in Settings",
        "rep.consumo_valor": "{consumo} {unidad}/100 km",
        "rep.apuntar": "Log a fill-up",
        "rep.fecha": "Date",
        "rep.litros": "Amount ({unidad})",
        "rep.precio": "Price (€/{unidad})",
        "rep.km": "Odometer (km, optional)",
        "rep.lleno": "I filled the tank",
        "rep.guardar": "Save fill-up",
        "rep.privado": "Stored only in this browser: Pumpcast never sees it. If you switch phones or clear "
                       "your browser data it is lost, so export a copy now and then.",
        "rep.historial": "History",
        "rep.vacio": "No fill-ups logged yet.",
        "rep.ahorro_titulo": "What you've saved",
        "rep.ahorro_bien": "saved versus your area's average (12 months)",
        "rep.ahorro_mal": "paid above your area's average (12 months)",
        "rep.ahorro_nota": "Compares what you paid in {n} fill-ups with that day's {comb} average in your "
                           "area.",
        "rep.ahorro_sin": "Once you log fill-ups, you'll see here how much you save versus your area's "
                          "average.",
        "rep.frente_media": "{dif}¢/{unidad} versus the average",
        "fav.novedades": "Your favourites today",
        "fav.bajado": "<b>{nombre}</b> is down {cts}¢ {cuando}",
        "fav.subido": "<b>{nombre}</b> is up {cts}¢ {cuando}",
        "fav.ayer": "since yesterday",
        "fav.dias": "in {n} days",
        "coche.titulo": "Car mode",
        "coche.salir": "Leave car mode",
        "coche.ir": "Go",
        "coche.buscando": "Finding where you are…",
        "coche.desde_ajustes": "From your location in Settings",
        "coche.aqui": "From where you are",
        "coche.otras": "Others nearby",
        "coche.nada": "No stations with {comb} within {radio} km.",
        "coche.pantalla": "The screen stays on while this is open.",
        "coche.actualizar": "Refresh",
        "bien.titulo": "Welcome",
        "bien.texto": "Three taps and you're done. What you choose is stored only in this browser.",
        "bien.paso": "Step {n} of 3",
        "bien.donde": "Where should we look?",
        "bien.gps": "Use where I am",
        "bien.o": "or type an address",
        "bien.que": "What do you fill up with?",
        "bien.radio": "How far would you go?",
        "bien.km": "{n} km",
        "bien.empezar": "Start",
        "bien.atras": "Back",
        "bien.lista": "Location set ✓",
        "bien.sin_js": "To choose where to look, go to Settings.",
        "rep.exportar": "Export copy",
        "rep.importar": "Import copy",
        "rep.error": "Check the amount and the price (and the km, if you added them).",
        "rep.borrar": "Delete",
        "rep.borrar_seguro": "Delete this fill-up?",
        "rep.importados": "Imported {n} fill-ups.",
        "rep.importar_mal": "That file isn't a Pumpcast copy.",
        "rep.lleno_corto": "full",
        "rep.km_corto": "{km} km",
        "voz.titulo": "With Siri or your assistant",
        "voz.intro": "Ask for a station without touching your phone: say <b>“Hey Siri, cheap fuel”</b> and "
                     "your maps app opens with directions to the cheapest one nearby that's open now. Made "
                     "for the car.",
        "voz.ajustes": "It searches within your Settings radius ({radio} km) for your fuel ({comb}).",
        "voz.iphone": "iPhone and CarPlay: with Siri",
        "voz.instalar": "Install the shortcut",
        "voz.atajo_viene": "It comes set up for {comb} and {app}.",
        "voz.atajo_cambiar": "For your settings, after installing it edit the shortcut's address and change "
                             "<code>{de}</code> to <code>{a}</code>.",
        "voz.o_crealo": "Or make it yourself in a couple of minutes:",
        "voz.paso1": "Open the <b>Shortcuts</b> app and tap <b>+</b> to make a new one.",
        "voz.paso2": "Add <b>Get Current Location</b>.",
        "voz.b2": "Add <b>Get Contents of URL</b> and paste this address (tap it to copy):",
        "voz.b2_nota": "Replace LAT with your position: delete it, tap “Current Location” above the keyboard, "
                       "tap that variable and pick <b>Latitude</b>. Same for LON and <b>Longitude</b>.",
        "voz.b3": "Add <b>Open URLs</b>: it opens what the previous step returned, which is the route in your "
                  "maps app.",
        "voz.permiso": "Apple Maps shows the route and you tap “Go”; Google Maps and Waze start on their own. "
                       "With the phone locked, iOS may ask you to unlock it.",
        "voz.simple_titulo": "One-action version",
        "voz.simple": "Easier to make: just <b>Open URLs</b> with this address. But it opens Safari, which "
                      "asks for your location (Settings › Apps › Safari › Location › Allow, so it stops "
                      "asking) and, before opening the map, iOS asks “Open this page in…?”: you have to tap "
                      "“Open”.",
        "voz.paso3": "Name it <b>Cheap fuel</b> (or whatever you want to say) and save it. Done: “Hey Siri, "
                     "cheap fuel”.",
        "voz.otros": "For another maps app, add <code>&amp;mapa=google</code>, <code>&amp;mapa=waze</code> or "
                     "<code>&amp;mapa=apple</code> at the end. For the nearest instead of the cheapest, "
                     "<code>&amp;orden=distancia</code>; for the best value counting the trip, "
                     "<code>&amp;orden=compensa</code>.",
        "voz.avanzado_titulo": "Have Siri read out the price",
        "voz.avanzado": "With a few more actions, Siri answers (“The cheapest within 10 km is Ballenoil, 1.4 "
                        "km away: 1.729 euros a litre”) and then opens the map. This way Safari's permission "
                        "isn't needed either:",
        "voz.a1": "Add <b>Get Current Location</b>.",
        "voz.a2": "Add <b>Get Contents of URL</b> with this address, replacing LAT and LON with the "
                  "location's <b>Latitude</b> and <b>Longitude</b> variables:",
        "voz.a3": "Add <b>Get Dictionary Value</b> with the key <b>frase</b>, then the Speak Text action.",
        "voz.a4": "Add <b>Get Dictionary Value</b> again, with the key <b>apple</b> (or <b>google</b>, "
                  "<b>waze</b>) and <b>Contents of URL</b> as the dictionary. Finish with <b>Open URLs</b>.",
        "voz.android": "Android: one tap away",
        "voz.android_texto": "Google doesn't let websites add voice commands to its assistant. The handiest "
                             "option: install Pumpcast on your home screen, long-press its icon and pick "
                             "<b>Cheapest nearby</b>; you can drag that shortcut onto the screen to have it "
                             "one tap away. It opens Google Maps already navigating there.",
        "voz.probar": "Try it now",
        "voz.atajo": "Cheapest nearby",
        "voz.buscando": "Finding where you are…",
        "voz.abrir_app": "Open Pumpcast",
        "pasar.titulo": "Move to another phone",
        "pasar.intro": "Take your settings, favourites and fill-ups to another phone or browser, no account "
                       "needed: scan the code with the other phone's camera or send yourself the link.",
        "pasar.lleva": "It carries {que}.",
        "pasar.ajustes": "your settings and location",
        "pasar.favoritas": "{n} favourites",
        "pasar.repostajes": "{n} fill-ups",
        "pasar.y": "and ",
        "pasar.nada": "Nothing to move yet: choose your location in Settings.",
        "pasar.qr_aria": "QR code with the link to move your data",
        "pasar.grande": "Too much data for a QR code: use the link.",
        "pasar.compartir": "Share the link",
        "pasar.copiar": "Copy the link",
        "pasar.privado": "Everything travels inside the link, after the “#”: that part never reaches the "
                         "server. Anyone with the link can see your location, so only send it to yourself.",
        "pasar.importar_titulo": "Bring from another phone",
        "pasar.importar_intro": "This link brings",
        "pasar.importar_aviso": "It replaces this phone's settings and favourites; fill-ups are added to any "
                                "already here.",
        "pasar.importar_boton": "Import on this phone",
        "pasar.importado": "Done: everything is on this phone now.",
        "pasar.importar_mal": "This link is incomplete or isn't from Pumpcast.",
        "pasar.ir_inicio": "Go to Pumpcast",
        "voz.precio": "The cheapest within {radio} km is {nombre}, in {municipio}, {distancia} away: {precio} "
                      "euros a {unidad}.",
        "voz.distancia": "The nearest is {nombre}, in {municipio}, {distancia} away: {precio} euros a "
                         "{unidad}.",
        "voz.compensa": "The best value within {radio} km is {nombre}, in {municipio}, {distancia} away: "
                        "{precio} euros a {unidad}.",
        "voz.nada": "I can't find any stations with prices within {radio} km.",
        "voz.fuera": "That location is outside Spain, and Pumpcast only has stations in Spain.",
        "voz.unidad_l": "litre",
        "voz.unidad_kg": "kilo",
        "voz.hor_24h": "It's open 24 hours.",
        "voz.hor_cierra": "It closes at {hora}.",
        "voz.hor_abre": "It's closed now; it opens at {hora}.",
        "voz.hor_cerrada": "It's closed now.",

        "prev.titulo": "Fill up today or wait?",
        "prev.provincia": "Based on prices across the province of {provincia}.",
        "prev.nombre_gasoil": "Wholesale diesel", "prev.nombre_gasolina": "Wholesale gasoline",
        "prev.semana_hasta": "week to {fecha}",
        "prev.acierta": "Right {pct}% of the time; always saying “No rush”, {base}%.",
        "prev.detalles": "How is it worked out?",
        "prev.como": "The forecast looks at how much wholesale fuel (Brent, for gas fuels) went up or down in "
                     "the latest published week and how much prices in your province moved: pumps follow the "
                     "market, rise faster than they fall, and prices have momentum.",
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
        "aj.mapa": "Maps app for directions",
        "aj.mapa_preguntar": "Ask every time",
        "aj.mapa_google": "Google Maps",
        "aj.mapa_apple": "Apple Maps",
        "aj.mapa_waze": "Waze",
        "voz.elegir_una_vez": "To skip this choice, set your app in <a href=\"/ajustes\">Settings</a> and copy "
                              "the shortcut address again from <a href=\"/voz\">With Siri</a>.",
        "voz.con_app": "The address already opens <b>{app}</b>, the maps app in your Settings. If you change "
                       "it, copy it again.",
        "voz.sin_app": "This way it asks which app to use every time. To go straight there, pick your maps "
                       "app in <a href=\"/ajustes\">Settings</a> and come back to copy the address.",
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

"""Pumpcast: la web y la tarea de fondo en un solo proceso."""
from __future__ import annotations

import asyncio
import logging
import threading
import urllib.parse
from contextlib import asynccontextmanager
from datetime import datetime, timedelta
from functools import partial
from pathlib import Path
from statistics import mean

from fastapi import FastAPI, HTTPException, Request
from fastapi.exception_handlers import http_exception_handler
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import JSONResponse, PlainTextResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from jinja2 import pass_context
from starlette.exceptions import HTTPException as StarletteHTTPException

from . import (avisos, config, copias, db, formato, horario, i18n, marcas, mercado, prediccion, preferencias, repo,
               seguridad, tareas)

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")

AQUI = Path(__file__).parent
templates = Jinja2Templates(directory=AQUI / "templates")


def _con_idioma(funcion):
    """Un filtro de Jinja que formatea según el idioma de la página."""
    @pass_context
    def filtro(ctx, valor, *args):
        return funcion(valor, *args, lang=ctx.get("lang", "es"))
    return filtro


templates.env.filters.update(
    euros=_con_idioma(formato.euros), moneda=_con_idioma(formato.moneda), centimos=_con_idioma(formato.centimos),
    km=_con_idioma(formato.km), fecha_corta=_con_idioma(formato.fecha_corta), dia=_con_idioma(formato.dia), numero=_con_idioma(formato.numero),
    porcentaje=_con_idioma(formato.porcentaje), titulo=formato.titulo)
templates.env.globals.update(idiomas=i18n.NOMBRES, mapas=config.MAPAS)


@asynccontextmanager
async def vida(_app: FastAPI):
    db.iniciar()
    tarea = None if config.SIN_TAREAS else asyncio.create_task(tareas.bucle())
    yield
    if tarea:
        tarea.cancel()


app = FastAPI(title="Pumpcast", lifespan=vida, docs_url=None, redoc_url=None, openapi_url=None)
app.middleware("http")(seguridad.middleware)
app.add_middleware(GZipMiddleware, minimum_size=1000)     # menos subida por el túnel: las páginas van comprimidas
app.mount("/static", StaticFiles(directory=AQUI / "static"), name="static")


def _idioma(request: Request, pref: dict | None) -> str:
    return i18n.elegir(pref["idioma"] if pref else "auto", request.headers.get("accept-language"))


def _elegir(request: Request, c: str | None) -> tuple[dict | None, dict, str]:
    """Las preferencias del visitante (None si aún no ha dicho dónde está), lo que se usa para
    pintar (con los valores por defecto si no hay) y el combustible."""
    pref = preferencias.leer(request)
    aj = pref or dict(config.PREFERENCIAS_POR_DEFECTO)
    return pref, aj, (c if c in config.COMBUSTIBLES else aj["combustible"])


def _contexto(request: Request, pagina: str, pref: dict | None, aj: dict, comb: str, **datos) -> dict:
    lang = _idioma(request, pref)
    return {"pagina": pagina, "aj": aj, "comb": comb, "lang": lang, "t": partial(i18n.t, lang),
            "js": i18n.para_js(lang), "nombre_comb": i18n.t(lang, "comb." + comb),
            "combustibles": list(config.COMBUSTIBLES), "version": config.VERSION,
            "nonce": request.state.nonce, "ultima": repo.ultima_lectura(), "sin_ubicacion": pref is None,
            "litros": float(aj["litros"]), "unidad": config.unidad(comb),
            "tema": (pref or {}).get("tema", "auto"), **datos}


def _pagina(request: Request, plantilla: str, pagina: str, pref: dict | None, aj: dict, comb: str,
            status_code: int = 200, **datos):
    return templates.TemplateResponse(request, plantilla, _contexto(request, pagina, pref, aj, comb, **datos),
                                      status_code=status_code)


def _prevision(aj: dict, comb: str, lang: str) -> dict:
    p = prediccion.prevision(repo.provincia_de(float(aj["lat"]), float(aj["lon"])), comb, float(aj["litros"]))
    if p["lista"]:
        p["titulo"] = prediccion.titulo(p, lang)
        p["frase"] = prediccion.frase(p, lang)
    return p


ORDENAR = {"precio": lambda e: (e["precio"], e["distancia"]), "distancia": lambda e: e["distancia"],
           "compensa": lambda e: e["con_viaje"]}


def _ordenadas(aj: dict, comb: str) -> tuple[list[dict], list[dict]]:
    """Las de alrededor en el orden elegido, y las que están abiertas (lo que no se sabe cuenta
    como abierto; si todas están cerradas, todas). La destacada es la primera abierta."""
    lista = _con_horario(repo.cercanas(aj, comb))
    litros, consumo = float(aj["litros"]), float(aj["consumo"])
    for e in lista:
        # Lo que cuesta de verdad: el repostaje más el combustible de ir y volver.
        e["con_viaje"] = e["precio"] * (litros + 2 * e["distancia"] * config.RODEO * consumo / 100)
    lista.sort(key=ORDENAR[aj["orden"]])
    return lista, [e for e in lista if e["abierta"] is not False] or lista


@app.get("/")
def inicio(request: Request, c: str | None = None, orden: str | None = None):
    pref, aj, comb = _elegir(request, c)
    if not pref:
        return _pagina(request, "inicio.html", "inicio", pref, aj, comb, lista=[])
    if orden in config.ORDENES and orden != pref["orden"]:
        pref = aj = {**pref, "orden": orden}            # se queda para la próxima vez (ver abajo)
    lista, abiertas = _ordenadas(aj, comb)
    litros = float(aj["litros"])
    media = mean(e["precio"] for e in lista) if lista else None
    mejor = abiertas[0] if abiertas else None
    ahorro = (media - mejor["precio"]) * litros if mejor else None
    otro = "distancia" if aj["orden"] == "precio" else "precio"
    secundaria = min(abiertas, key=ORDENAR[otro]) if abiertas else None
    ids_favoritas = preferencias.favoritas(request)
    favoritas = _con_horario(repo.favoritas(aj, comb, ids_favoritas))
    respuesta = _pagina(request, "inicio.html", "inicio", pref, aj, comb, lista=lista, mejor=mejor,
                        resto=[e for e in lista if e is not mejor][:20], total=len(lista), media=media, ahorro=ahorro,
                        favoritas=favoritas, ids_favoritas=ids_favoritas, otro=otro,
                        secundaria=secundaria if secundaria is not mejor else None,
                        prevision=_prevision(aj, comb, _idioma(request, pref)))
    if orden == aj["orden"]:
        preferencias.guardar(respuesta, request, aj)
    return respuesta


def _con_horario(lista: list[dict]) -> list[dict]:
    """Añade a cada gasolinera si está abierta ahora (None si su horario no se entiende)."""
    ahora = datetime.now(config.TZ)
    for e in lista:
        e["estado"] = horario.estado(e.get("horario"), ahora, e.get("provincia_id"))
        e["abierta"] = e["estado"]["abierta"] if e["estado"] else None
    return lista


def _para_mapa(lista: list[dict]) -> list[dict]:
    return [{k: e[k] for k in ("id", "rotulo", "municipio", "lat", "lon", "precio", "distancia", "abierta", "estado")}
            for e in _con_horario(lista)]


@app.get("/mapa")
def mapa(request: Request, c: str | None = None):
    pref, aj, comb = _elegir(request, c)
    if not pref:
        return _pagina(request, "mapa.html", "mapa", pref, aj, comb, estaciones=[], escala={})
    radio = float(aj["radio_km"])
    todas = repo.cercanas(aj, comb, radio_km=min(max(3 * radio, 25), 2 * config.MAX_RADIO_KM))
    cerca = [e["precio"] for e in todas if e["distancia"] <= radio] or [e["precio"] for e in todas]
    escala = {"min": min(cerca), "max": max(cerca), "media": mean(cerca)} if cerca else {"min": 0, "max": 0, "media": 0}
    lang = _idioma(request, pref)
    estaciones = _para_mapa(todas)
    for e in estaciones:
        est = e["estado"]
        e["horario"] = i18n.t(lang, "hor." + est["clave"], hora=est["hora"]) if est else ""
        e["insignia"] = marcas.insignia(e["rotulo"])
    return _pagina(request, "mapa.html", "mapa", pref, aj, comb, estaciones=estaciones, escala=escala,
                   favoritas=preferencias.favoritas(request))


@app.get("/estacion/{estacion_id}")
def ver_estacion(request: Request, estacion_id: int, c: str | None = None):
    pref, aj, comb = _elegir(request, c)
    e = repo.estacion(estacion_id)
    if not e:
        raise HTTPException(404, i18n.t(_idioma(request, pref), "estacion.no_existe"))
    e["distancia"] = repo.distancia_km(float(aj["lat"]), float(aj["lon"]), e["lat"], e["lon"]) if pref else None
    historial = repo.historial(estacion_id, comb)
    zona = {}
    if pref:
        zona = {f["fecha"]: f["media"] for f in repo.serie_zona(aj, comb)}
    grafica = {"fechas": [h["fecha"] for h in historial], "precio": [h["precio"] for h in historial],
               "zona": [zona.get(h["fecha"]) for h in historial] if zona else []}
    _con_horario([e])
    return _pagina(request, "estacion.html", "mapa", pref, aj, comb, e=e, favorita=estacion_id in preferencias.favoritas(request),
                   precios=repo.precios_actuales(estacion_id), grafica=grafica)


@app.post("/favorita/{estacion_id}")
def cambiar_favorita(request: Request, estacion_id: int):
    """Marca o desmarca una favorita y vuelve a donde estaba (sin JavaScript también vale)."""
    if not repo.estacion(estacion_id):
        raise HTTPException(404)
    ids = preferencias.favoritas(request)
    ids = [i for i in ids if i != estacion_id] if estacion_id in ids else [estacion_id, *ids]
    volver = urllib.parse.urlsplit(request.headers.get("referer", ""))
    destino = volver.path + (f"?{volver.query}" if volver.query else "") if volver.path.startswith("/") else "/"
    respuesta = RedirectResponse(destino if not destino.startswith("//") else "/", status_code=303)
    preferencias.guardar_favoritas(respuesta, request, ids)
    return respuesta


def _brent_para_grafica(serie: list[dict]) -> list[float | None]:
    brent = mercado.brent_euros()
    return [round(brent[f["fecha"]], 2) if f["fecha"] in brent else None for f in serie]


DIAS_MARCAS = 30
MARCAS_POR_PUNTA = 5


@app.get("/tendencia")
def tendencia(request: Request, c: str | None = None):
    pref, aj, comb = _elegir(request, c)
    if not pref:
        return _pagina(request, "tendencia.html", "tendencia", pref, aj, comb, serie=[])
    serie = repo.serie_zona(aj, comb, dias=90)
    cambios = {}
    if serie:
        por_fecha = {f["fecha"]: f["media"] for f in serie}
        hoy = datetime.fromisoformat(serie[-1]["fecha"])
        for nombre, dias in (("semana", 7), ("mes", 30)):
            antes = por_fecha.get((hoy - timedelta(days=dias)).date().isoformat())
            cambios[nombre] = serie[-1]["media"] - antes if antes is not None else None
    semana = repo.por_dia_semana(serie)
    con_datos = [d for d in semana if d["media"] is not None]
    brent = _brent_para_grafica(serie)
    mejor_dia = min(con_datos, key=lambda d: d["media"])["dia"] if len(serie) >= 14 and con_datos else None
    por_marca = repo.marcas(aj, comb, dias=DIAS_MARCAS)
    if len(por_marca) > 2 * MARCAS_POR_PUNTA:           # las más baratas y las más caras; el medio, fuera
        por_marca = por_marca[:MARCAS_POR_PUNTA] + [None] + por_marca[-MARCAS_POR_PUNTA:]
    return _pagina(request, "tendencia.html", "tendencia", pref, aj, comb, serie=serie, semana=semana,
                   marcas=por_marca, dias_marcas=DIAS_MARCAS,
                   cambios=cambios, mejor_dia=mejor_dia, prevision=_prevision(aj, comb, _idioma(request, pref)),
                   brent=brent, brent_hasta=max((f["fecha"] for f, b in zip(serie, brent) if b is not None), default=None))


@app.get("/repostajes")
def repostajes(request: Request, c: str | None = None, estacion: int | None = None):
    """Los repostajes del visitante: se apuntan y se guardan solo en su navegador (repostajes.js).
    Desde la ficha de una gasolinera llega con ella para rellenar el precio."""
    pref, aj, comb = _elegir(request, c)
    e = repo.estacion(estacion) if estacion else None
    precio = repo.precios_actuales(e["id"]).get(comb) if e else None
    nombre = f'{formato.titulo(e["rotulo"])} · {e["municipio"]}' if e else ""
    return _pagina(request, "repostajes.html", "repostajes", pref, aj, comb, precio=precio, nombre=nombre)


def _sin_guardar(respuesta):
    """Páginas con tus datos o tu posición: ni cachés por el camino ni la copia sin conexión (sw.js)."""
    respuesta.headers["Cache-Control"] = "no-store"
    return respuesta


# --- Llevarse los ajustes, las favoritas y los repostajes a otro móvil --------------------

@app.get("/pasar")
def pasar(request: Request):
    """En el móvil de origen, un enlace (y su QR) con todo; en el de destino, el mismo enlace lo
    importa. Lo que se lleva va detrás de «#», que el navegador nunca manda al servidor."""
    pref, aj, comb = _elegir(request, None)
    datos = {"p": preferencias.para_cookie(pref) if pref else "", "f": preferencias.favoritas(request)}
    return _sin_guardar(_pagina(request, "pasar.html", "pasar", pref, aj, comb, mios=datos))


@app.post("/pasar")
async def pasar_importar(request: Request):
    """Guarda en este móvil los ajustes y las favoritas que vienen del otro (los repostajes no
    pasan por aquí: van directos al almacenamiento del navegador)."""
    datos = await request.json()
    pref = preferencias.leer_texto(str(datos.get("p") or ""))
    ids = [int(x) for x in datos.get("f") or [] if str(x).isdigit()][:config.MAX_FAVORITAS]
    respuesta = JSONResponse({"ok": True, "ajustes": pref is not None, "favoritas": len(ids)},
                             headers={"Cache-Control": "no-store"})
    if pref:
        preferencias.guardar(respuesta, request, pref)
    if ids:
        preferencias.guardar_favoritas(respuesta, request, list(dict.fromkeys(ids)))
    return respuesta


# --- Con Siri, el asistente o un atajo: la mejor de alrededor sin abrir la app -----------

def _desde_aqui(request: Request, lat: float, lon: float, c: str | None, radio: float | None,
                orden: str | None) -> tuple[dict, str, str | None]:
    """Las preferencias para buscar desde la posición que llega en la dirección (redondeada a unos
    100 m) en vez de la de la cookie. Lo que no venga sale de la cookie, si la hay (abierto desde
    Safari), o de los valores por defecto (un atajo no lleva cookies)."""
    pref, _, comb = _elegir(request, c)
    base = pref or dict(config.PREFERENCIAS_POR_DEFECTO)
    valores = {**base, "lat": f"{lat:.3f}", "lon": f"{lon:.3f}", "combustible": comb,
               "radio_km": str(radio) if radio else base["radio_km"], "orden": orden or base["orden"]}
    aj, error = preferencias.validar(valores, preferencias.CAMPOS)
    return aj, comb, error


def _la_mejor(aj: dict, comb: str) -> dict | None:
    return (_ordenadas(aj, comb)[1] or [None])[0]


def _frase_voz(lang: str, e: dict | None, aj: dict, comb: str, error: str | None) -> str:
    """Lo que dice Siri: pensado para oírlo, sin símbolos."""
    t = partial(i18n.t, lang)
    if error:
        return t("voz.fuera" if error == "err.fuera" else error)
    if not e:
        return t("voz.nada", radio=formato.numero(float(aj["radio_km"]), 0, lang))
    frase = t("voz." + aj["orden"], nombre=formato.titulo(e["rotulo"]), municipio=formato.municipio(e["municipio"]),
              radio=formato.numero(float(aj["radio_km"]), 0, lang), distancia=formato.km(e["distancia"], lang),
              precio=formato.numero(e["precio"], 3, lang), unidad=t("voz.unidad_" + config.unidad(comb).lower()))
    if e["estado"]:
        frase += " " + t("voz.hor_" + e["estado"]["clave"], hora=e["estado"]["hora"])
    return frase


@app.get("/api/cerca")
def api_cerca(request: Request, lat: float, lon: float, c: str | None = None, radio: float | None = None,
              orden: str | None = None):
    """La mejor gasolinera de alrededor de un punto, con una frase para que la diga Siri y los
    enlaces para ir. Para los atajos de Siri (ver /voz) o quien quiera usarlo."""
    aj, comb, error = _desde_aqui(request, lat, lon, c, radio, orden)
    lang = _idioma(request, preferencias.leer(request))
    e = None if error else _la_mejor(aj, comb)
    datos = {"ok": e is not None, "frase": _frase_voz(lang, e, aj, comb, error)}
    if e:
        datos |= {"nombre": formato.titulo(e["rotulo"]), "municipio": e["municipio"],
                  "direccion": formato.titulo(e["direccion"]), "precio": e["precio"], "unidad": config.unidad(comb),
                  "combustible": comb, "distancia_km": round(e["distancia"], 2), "abierta": e["abierta"],
                  "lat": e["lat"], "lon": e["lon"], "ficha": f"{request.base_url}estacion/{e['id']}?c={comb}",
                  **{nombre: plantilla.format(lat=e["lat"], lon=e["lon"])
                     for nombre, plantilla in config.MAPAS_NAVEGAR.items()}}
    return JSONResponse(datos, headers={"Cache-Control": "no-store"})


@app.get("/ir")
def ir(request: Request, lat: float | None = None, lon: float | None = None, c: str | None = None,
       radio: float | None = None, orden: str | None = None, mapa: str | None = None, enlace: bool = False):
    """«Oye Siri, gasolinera barata»: abre la app de mapas camino de la mejor de alrededor. Si no
    trae la posición, la página la pide al navegador y vuelve aquí con ella.

    Con `enlace=1` no redirige: devuelve el enlace de la ruta en texto, para que lo abra el propio
    atajo («Abrir URL»). Abierto así, iOS va directo a la app de mapas; desde Safari, en cambio,
    pregunta «¿Abrir esta página en Waze?» porque no lo ha pedido un toque en la página."""
    pref, aj, comb = _elegir(request, c)
    lang = _idioma(request, pref)
    if enlace:
        return _enlace_ir(request, lat, lon, c, radio, orden, mapa)
    if lat is None or lon is None:
        return _sin_guardar(_pagina(request, "ir.html", "ir", pref, aj, comb, mensaje=None, destinos=None))
    aj_aqui, comb, error = _desde_aqui(request, lat, lon, c, radio, orden)
    e = None if error else _la_mejor(aj_aqui, comb)
    if not e:
        return _sin_guardar(_pagina(request, "ir.html", "ir", pref, aj, comb,
                                    mensaje=_frase_voz(lang, None, aj_aqui, comb, error), destinos=None))
    # La app: la de la dirección (el atajo no lleva cookies), si no la de Ajustes; si no hay, se pregunta.
    mapa = mapa if mapa in config.MAPAS_NAVEGAR else (pref or {}).get("mapa")
    destinos = {nombre: p.format(lat=e["lat"], lon=e["lon"]) for nombre, p in config.MAPAS_NAVEGAR.items()}
    if mapa not in destinos:
        return _sin_guardar(_pagina(request, "ir.html", "ir", pref, aj, comb,
                                    mensaje=_frase_voz(lang, e, aj_aqui, comb, None), destinos=destinos))
    return RedirectResponse(destinos[mapa], status_code=302, headers={"Cache-Control": "no-store"})


def _enlace_ir(request: Request, lat: float | None, lon: float | None, c: str | None, radio: float | None,
               orden: str | None, mapa: str | None) -> PlainTextResponse:
    """El enlace que abre el atajo. Si no puede ir directo (sin posición, sin gasolineras o sin app
    elegida), el de la página de /ir, que lo explica o deja elegir."""
    sin_enlace = {k: v for k, v in request.query_params.items() if k != "enlace"}
    pagina = f"{request.base_url}ir?{urllib.parse.urlencode(sin_enlace)}"
    if lat is None or lon is None or mapa not in config.MAPAS_NAVEGAR:
        return PlainTextResponse(pagina, headers={"Cache-Control": "no-store"})
    aj, comb, error = _desde_aqui(request, lat, lon, c, radio, orden)
    e = None if error else _la_mejor(aj, comb)
    destino = config.MAPAS_NAVEGAR[mapa].format(lat=e["lat"], lon=e["lon"]) if e else pagina
    return PlainTextResponse(destino, headers={"Cache-Control": "no-store"})


@app.get("/voz")
def voz(request: Request, c: str | None = None):
    """Cómo pedírselo a Siri (o tenerlo a un toque en Android)."""
    pref, aj, comb = _elegir(request, c)
    base = str(request.base_url)
    app_mapa = aj.get("mapa", "preguntar")
    con_app = f"&mapa={app_mapa}" if app_mapa in config.MAPAS_NAVEGAR else ""
    # El atajo ya hecho: qué tocar en su dirección si tu combustible o tu app no son los suyos.
    de, a = f"c={config.ATAJO_COMBUSTIBLE}&mapa={config.ATAJO_MAPA}", f"c={comb}&mapa={app_mapa if con_app else config.ATAJO_MAPA}"
    return _pagina(request, "voz.html", "voz", pref, aj, comb, url_ir=f"{base}ir?c={comb}{con_app}", app_mapa=app_mapa,
                   atajo=config.ATAJO_ICLOUD, atajo_de=de, atajo_a=a if a != de else None,
                   atajo_comb=i18n.t(_idioma(request, pref), "comb." + config.ATAJO_COMBUSTIBLE)
                   if config.ATAJO_COMBUSTIBLE in config.COMBUSTIBLES else config.ATAJO_COMBUSTIBLE,
                   atajo_app={"google": "Google Maps", "apple": "Apple Maps", "waze": "Waze"}.get(config.ATAJO_MAPA, config.ATAJO_MAPA),
                   url_enlace=f"{base}ir?c={comb}{con_app}&enlace=1&lat=LAT&lon=LON",
                   url_api=f"{base}api/cerca?c={comb}&lat=LAT&lon=LON")


# --- Ajustes de cada visitante (en su navegador) -----------------------------------------

@app.get("/ajustes")
def ver_ajustes(request: Request):
    pref, aj, comb = _elegir(request, None)
    return _pagina(request, "ajustes.html", "ajustes", pref, aj, comb, admin=False, error=None)


@app.post("/ajustes")
async def guardar_ajustes(request: Request):
    pref, _, _ = _elegir(request, None)
    valores, error = preferencias.validar(dict(await request.form()), preferencias.CAMPOS)
    if "application/json" in request.headers.get("accept", ""):
        # Ajustes guarda solo, a cada cambio, sin salir de la página.
        if error:
            return JSONResponse({"ok": False, "error": i18n.t(_idioma(request, pref), error)}, status_code=400)
        respuesta = JSONResponse({"ok": True})
        preferencias.guardar(respuesta, request, valores)
        return respuesta
    if error:
        aj = {**config.PREFERENCIAS_POR_DEFECTO, **valores}
        comb = aj["combustible"] if aj["combustible"] in config.COMBUSTIBLES else "g95"
        return _pagina(request, "ajustes.html", "ajustes", pref, aj, comb, status_code=400, admin=False, error=error)
    respuesta = RedirectResponse("/", status_code=303)
    preferencias.guardar(respuesta, request, valores)
    return respuesta


GPS_DECIMALES = 3            # ~100 m: de sobra para buscar en kilómetros, y nunca viaja la posición exacta
GPS_MOVIMIENTO_KM = 1        # por menos de esto no merece la pena recargar


@app.post("/ubicacion")
async def ubicacion_actual(request: Request):
    """Con «usar dónde estoy», el navegador manda aquí su posición al abrir la app y esto solo
    cambia su cookie. Llega en el cuerpo y no en la URL para que no quede en los registros."""
    pref = preferencias.leer(request)
    if pref is None or pref["gps"] != "1":
        return JSONResponse({"cambiada": False}, status_code=409)
    form = await request.form()
    try:
        lat, lon = (round(float(str(form.get(k, "")).replace(",", ".")), GPS_DECIMALES) for k in ("lat", "lon"))
    except ValueError:
        return JSONResponse({"cambiada": False, "error": "err.numero"}, status_code=400)
    valores, error = preferencias.validar({**pref, "lat": lat, "lon": lon}, preferencias.CAMPOS)
    if error:
        return JSONResponse({"cambiada": False, "error": error}, status_code=400)
    movido = repo.distancia_km(float(pref["lat"]), float(pref["lon"]), lat, lon)
    if movido < GPS_MOVIMIENTO_KM:
        return JSONResponse({"cambiada": False})
    respuesta = JSONResponse({"cambiada": True})
    preferencias.guardar(respuesta, request, valores)
    return respuesta


@app.post("/ajustes/olvidar")
def olvidar_ajustes():
    respuesta = RedirectResponse("/ajustes", status_code=303)
    preferencias.olvidar(respuesta)
    return respuesta


# --- Panel de administración: los avisos de Telegram del dueño ---------------------------
# No existe sin ADMIN_PASSWORD_HASH ni para lo que entra por Cloudflare (ver seguridad.py).

def _admin_disponible(request: Request) -> None:
    if not config.ADMIN_PASSWORD_HASH or seguridad.desde_internet(request):
        raise HTTPException(404)


def _pagina_admin(request: Request, plantilla: str, status_code: int = 200, **datos):
    pref, _, _ = _elegir(request, None)
    aj = repo.ajustes()
    comb = aj["combustible"] if aj["combustible"] in config.COMBUSTIBLES else "g95"
    return _pagina(request, plantilla, "ajustes", pref, aj, comb, status_code=status_code, admin=True, **datos)


def _entrar(request: Request, error: str | None = None, status_code: int = 200):
    return _pagina_admin(request, "admin_entrar.html", status_code=status_code, error=error,
                         con_codigo=seguridad.secreto_totp() is not None)


def _alta(request: Request, secreto: str, error: str | None = None, status_code: int = 200):
    return _pagina_admin(request, "admin_alta.html", status_code=status_code, error=error, secreto=secreto,
                         enlace=seguridad.enlace_totp(secreto))


def _con_sesion(request: Request):
    respuesta = RedirectResponse("/admin", status_code=303)
    seguridad.poner_cookie(respuesta, request, seguridad.COOKIE_ADMIN, seguridad.nueva_sesion(),
                           seguridad.HORAS_DE_SESION * 3600)
    respuesta.delete_cookie(seguridad.COOKIE_ALTA, path="/admin")
    return respuesta


@app.get("/admin")
def admin(request: Request, guardado: bool = False, prueba: str | None = None, lectura: str | None = None):
    _admin_disponible(request)
    if not seguridad.sesion_valida(request):
        return _entrar(request)
    return _pagina_admin(request, "ajustes.html", guardado=guardado, prueba=prueba, lectura=lectura, error=None,
                         brent_viejo=mercado.brent_viejo(mercado.ultimo_brent()), ultimo_brent=mercado.ultimo_brent(),
                         telegram=avisos.configurado())


@app.post("/admin/entrar")
async def admin_entrar(request: Request):
    _admin_disponible(request)
    if seguridad.bloqueado(request):
        return _entrar(request, "admin.bloqueado", 429)
    form = await request.form()
    clave, codigo = str(form.get("clave", "")), str(form.get("codigo", ""))
    if not await asyncio.to_thread(seguridad.comprobar_clave, clave, config.ADMIN_PASSWORD_HASH):
        seguridad.apuntar_fallo(request)
        return _entrar(request, "admin.error", 401)
    secreto = seguridad.secreto_totp()
    if secreto is None:                                   # primera vez: dar de alta el segundo paso
        ficha, nuevo = seguridad.nueva_alta()
        respuesta = _alta(request, nuevo)
        seguridad.poner_cookie(respuesta, request, seguridad.COOKIE_ALTA, ficha, seguridad.MINUTOS_DE_ALTA * 60)
        return respuesta
    if not seguridad.comprobar_totp(secreto, codigo):
        seguridad.apuntar_fallo(request)
        return _entrar(request, "admin.error", 401)
    return _con_sesion(request)


@app.post("/admin/alta")
async def admin_alta(request: Request):
    _admin_disponible(request)
    secreto = seguridad.alta_pendiente(request)
    if not secreto or seguridad.secreto_totp() is not None:
        return RedirectResponse("/admin", status_code=303)
    if seguridad.bloqueado(request):
        return _alta(request, secreto, "admin.bloqueado", 429)
    if not seguridad.comprobar_totp(secreto, str((await request.form()).get("codigo", ""))):
        seguridad.apuntar_fallo(request)
        return _alta(request, secreto, "admin.codigo_mal", 401)
    repo.guardar_secreto("totp", secreto)
    seguridad.terminar_alta(request)
    logging.getLogger("pumpcast").info("Verificación en dos pasos del panel activada")
    return _con_sesion(request)


def _exigir_sesion(request: Request) -> None:
    _admin_disponible(request)
    if not seguridad.sesion_valida(request):
        raise HTTPException(303, headers={"Location": "/admin"})


@app.post("/admin")
async def admin_guardar(request: Request):
    _exigir_sesion(request)
    form = await request.form()
    campos = tuple(k for k in config.AJUSTES_POR_DEFECTO if k not in ("aviso_diario", "avisos_chollo"))
    valores, error = preferencias.validar(dict(form), campos)
    valores["aviso_diario"] = "1" if form.get("aviso_diario") else "0"
    valores["avisos_chollo"] = "1" if form.get("avisos_chollo") else "0"
    if error:
        pref, _, _ = _elegir(request, None)
        aj = {**repo.ajustes(), **valores}
        comb = aj["combustible"] if aj["combustible"] in config.COMBUSTIBLES else "g95"
        return _pagina(request, "ajustes.html", "ajustes", pref, aj, comb, status_code=400, admin=True,
                       error=error, telegram=avisos.configurado())
    await asyncio.to_thread(repo.guardar_ajustes, valores)
    return RedirectResponse("/admin?guardado=1", status_code=303)


@app.post("/admin/prueba")
def admin_prueba(request: Request):
    _exigir_sesion(request)
    try:
        avisos.enviar(i18n.t(avisos.idioma(repo.ajustes()), "tg.prueba"))
        resultado = "ok"
    except Exception:  # noqa: BLE001
        resultado = "error"
    return RedirectResponse(f"/admin?prueba={resultado}", status_code=303)


_leyendo = threading.Lock()


@app.post("/admin/actualizar")
def admin_actualizar(request: Request):
    _exigir_sesion(request)
    if not _leyendo.acquire(blocking=False):              # ya hay una lectura en marcha
        return RedirectResponse("/admin?lectura=ok", status_code=303)
    try:
        resultado = "ok" if tareas.leer_ahora() else "error"
    finally:
        _leyendo.release()
    return RedirectResponse(f"/admin?lectura={resultado}", status_code=303)


@app.post("/admin/salir")
def admin_salir(request: Request):
    _admin_disponible(request)
    seguridad.cerrar_sesion(request)
    respuesta = RedirectResponse("/", status_code=303)
    respuesta.delete_cookie(seguridad.COOKIE_ADMIN, path="/admin")
    return respuesta


# --- App instalable (PWA) ----------------------------------------------------------------

@app.get("/manifest.webmanifest")
def manifest(request: Request):
    lang = _idioma(request, preferencias.leer(request))
    return JSONResponse({
        "name": "Pumpcast", "short_name": "Pumpcast", "lang": lang,
        "description": i18n.t(lang, "manifest.descripcion"),
        "start_url": "/", "scope": "/", "display": "standalone",
        # Manteniendo pulsado el icono (Android): a un toque de ir a la mejor de alrededor.
        "shortcuts": [{"name": i18n.t(lang, "voz.atajo"), "url": f"/ir?c={_elegir(request, None)[2]}",
                       "icons": [{"src": "/static/iconos/icono-192.png", "sizes": "192x192"}]}],
        "background_color": "#f4f5f4", "theme_color": "#0f766e",
        "icons": [
            {"src": "/static/iconos/icono-192.png", "sizes": "192x192", "type": "image/png"},
            {"src": "/static/iconos/icono-512.png", "sizes": "512x512", "type": "image/png"},
            {"src": "/static/iconos/icono-recortable-512.png", "sizes": "512x512", "type": "image/png",
             "purpose": "maskable"},
        ],
    }, media_type="application/manifest+json")


@app.get("/sw.js")
def service_worker(request: Request):
    lang = _idioma(request, preferencias.leer(request))
    return templates.TemplateResponse(request, "sw.js", {"version": config.VERSION, "lang": lang,
                                                         "aviso": i18n.t(lang, "off.aviso", fecha="{fecha}")},
                                      media_type="text/javascript", headers={"Cache-Control": "no-cache"})


@app.get("/legal")
def legal(request: Request):
    pref, aj, comb = _elegir(request, None)
    contacto = config.CONTACTO or config.REPOSITORIO + "/issues"
    enlace = ("mailto:" + contacto) if "@" in contacto and "://" not in contacto else contacto
    return _pagina(request, "legal.html", "legal", pref, aj, comb, titular=config.TITULAR,
                   contacto=contacto, enlace_contacto=enlace, repositorio=config.REPOSITORIO)


@app.exception_handler(StarletteHTTPException)
async def error_http(request: Request, exc: StarletteHTTPException):
    """Una página que no existe se ve como el resto de la web, no como un JSON pelado."""
    if exc.status_code != 404 or request.url.path.startswith("/api/") or not hasattr(request.state, "nonce"):
        return await http_exception_handler(request, exc)
    pref, aj, comb = _elegir(request, None)
    return _pagina(request, "no_encontrada.html", "error", pref, aj, comb, status_code=404)


@app.get("/sin-conexion")
def sin_conexion(request: Request):
    pref, aj, comb = _elegir(request, None)
    return _pagina(request, "sin_conexion.html", "", pref, aj, comb)


# --- Para máquinas -----------------------------------------------------------------------
# La ubicación va en la URL (?lat=..&lon=..&radio_km=..) o, si no, en la cookie de Ajustes.

def _ubicacion_api(request: Request) -> dict:
    q = request.query_params
    if "lat" in q or "lon" in q:
        valores, error = preferencias.validar({**config.PREFERENCIAS_POR_DEFECTO, **q}, preferencias.CAMPOS)
        if error:
            raise HTTPException(400, i18n.t(_idioma(request, None), error))
        return valores
    pref = preferencias.leer(request)
    if not pref:
        raise HTTPException(400, i18n.t(_idioma(request, None), "api.sin_ubicacion"))
    return pref


@app.get("/api/estaciones")
def api_estaciones(request: Request, c: str | None = None):
    aj = _ubicacion_api(request)
    comb = c if c in config.COMBUSTIBLES else aj["combustible"]
    return {"combustible": comb, "estaciones": _para_mapa(repo.cercanas(aj, comb))}


@app.get("/api/resumen")
def api_resumen(request: Request, c: str | None = None):
    """Lo de la pantalla de inicio en JSON, para bots y atajos: media, la más barata y el semáforo."""
    aj = _ubicacion_api(request)
    comb = c if c in config.COMBUSTIBLES else aj["combustible"]
    lang = _idioma(request, aj)
    lista = repo.cercanas(aj, comb)
    p = _prevision(aj, comb, lang)
    return {"combustible": i18n.t(lang, "comb." + comb),
            "media": mean(e["precio"] for e in lista) if lista else None,
            "mejor": _para_mapa(lista[:1])[0] if lista else None,
            "litros": float(aj["litros"]),
            "coste": round(lista[0]["precio"] * float(aj["litros"]), 2) if lista else None,
            "prevision": {k: p[k] for k in ("semaforo", "icono", "titulo", "frase", "cambio")} if p["lista"] else None}


@app.get("/salud")
def salud():
    """Para Uptime Kuma (palabra clave "ok") y el healthcheck del contenedor."""
    ultima = repo.ultima_lectura()
    estado = "sin-datos"
    if ultima:
        edad = datetime.now(config.TZ) - datetime.fromisoformat(ultima["momento"])
        estado = "ok" if edad < timedelta(hours=3) else "datos-viejos"
    brent = mercado.ultimo_brent()
    productos = mercado.ultimos_productos()
    if estado == "ok" and mercado.brent_viejo(brent):
        estado = "brent-viejo"
    # Sin gasóleo o gasolina la previsión sigue con el Brent, pero acierta menos: que avise igual.
    if estado == "ok" and any(mercado.brent_viejo(f) for f in productos.values()):
        estado = "productos-viejos"
    return JSONResponse({"estado": estado, "version": config.VERSION,
                         "ultima_lectura": ultima["momento"] if ultima else None, "ultimo_brent": brent,
                         "ultimos_productos": productos})

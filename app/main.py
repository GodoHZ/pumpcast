"""Pumpcast: la web y la tarea de fondo en un solo proceso."""
from __future__ import annotations

import asyncio
import json
import logging
import re
import urllib.parse
import urllib.request
from contextlib import asynccontextmanager
from datetime import datetime, timedelta
from functools import partial
from pathlib import Path
from statistics import mean

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from jinja2 import pass_context

from . import avisos, config, db, formato, i18n, mercado, prediccion, repo, tareas

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
    km=_con_idioma(formato.km), fecha_corta=_con_idioma(formato.fecha_corta), numero=_con_idioma(formato.numero),
    titulo=formato.titulo)


@asynccontextmanager
async def vida(_app: FastAPI):
    db.iniciar()
    tarea = None if config.SIN_TAREAS else asyncio.create_task(tareas.bucle())
    yield
    if tarea:
        tarea.cancel()


app = FastAPI(title="Pumpcast", lifespan=vida, docs_url=None, redoc_url=None, openapi_url=None)
app.mount("/static", StaticFiles(directory=AQUI / "static"), name="static")


def _idioma(request: Request, aj: dict) -> str:
    navegador = i18n.del_navegador(request.headers.get("accept-language"))
    if aj["idioma"] == "auto" and aj["idioma_visto"] != navegador:
        repo.guardar_ajustes({"idioma_visto": navegador})        # para los avisos de Telegram
    return i18n.elegir(aj["idioma"], request.headers.get("accept-language"))


def _elegir(c: str | None) -> tuple[dict, str]:
    aj = repo.ajustes()
    return aj, (c if c in config.COMBUSTIBLES else aj["combustible"])


def _contexto(request: Request, pagina: str, aj: dict, comb: str, **datos) -> dict:
    lang = _idioma(request, aj)
    return {"pagina": pagina, "aj": aj, "comb": comb, "lang": lang, "t": partial(i18n.t, lang),
            "js": i18n.para_js(lang), "nombre_comb": i18n.t(lang, "comb." + comb),
            "combustibles": list(config.COMBUSTIBLES), "version": config.VERSION,
            "ultima": repo.ultima_lectura(), "sin_provincia": not repo.provincias(aj), **datos}


def _pagina(request: Request, plantilla: str, pagina: str, aj: dict, comb: str, **datos):
    return templates.TemplateResponse(request, plantilla, _contexto(request, pagina, aj, comb, **datos))


def _prevision(aj: dict, comb: str, lang: str) -> dict:
    p = prediccion.prevision(aj, comb)
    if p["lista"]:
        p["titulo"] = prediccion.titulo(p, lang)
        p["frase"] = prediccion.frase(p, lang)
    return p


@app.get("/")
def inicio(request: Request, c: str | None = None):
    aj, comb = _elegir(c)
    lista = repo.cercanas(aj, comb)
    media = mean(e["precio"] for e in lista) if lista else None
    ahorro = (media - lista[0]["precio"]) * float(aj["litros"]) if lista else None
    lang = _idioma(request, aj)
    return _pagina(request, "inicio.html", "inicio", aj, comb, lista=lista[:20], total=len(lista),
                   media=media, ahorro=ahorro, prevision=_prevision(aj, comb, lang))


def _para_mapa(lista: list[dict]) -> list[dict]:
    return [{k: e[k] for k in ("id", "rotulo", "municipio", "lat", "lon", "precio", "distancia")}
            for e in lista]


@app.get("/mapa")
def mapa(request: Request, c: str | None = None):
    aj, comb = _elegir(c)
    todas = repo.cercanas(aj, comb, radio_km=10_000)
    cerca = [e["precio"] for e in todas if e["distancia"] <= float(aj["radio_km"])] or [e["precio"] for e in todas]
    escala = {"min": min(cerca), "max": max(cerca)} if cerca else {"min": 0, "max": 0}
    return _pagina(request, "mapa.html", "mapa", aj, comb, estaciones=_para_mapa(todas), escala=escala)


@app.get("/estacion/{estacion_id}")
def ver_estacion(request: Request, estacion_id: int, c: str | None = None):
    aj, comb = _elegir(c)
    e = repo.estacion(estacion_id)
    if not e:
        raise HTTPException(404, i18n.t(_idioma(request, aj), "estacion.no_existe"))
    e["distancia"] = repo.distancia_km(float(aj["lat"]), float(aj["lon"]), e["lat"], e["lon"])
    zona = {f["fecha"]: f["media"] for f in repo.serie_zona(aj, comb)}
    historial = repo.historial(estacion_id, comb)
    grafica = {"fechas": [h["fecha"] for h in historial], "precio": [h["precio"] for h in historial],
               "zona": [zona.get(h["fecha"]) for h in historial]}
    return _pagina(request, "estacion.html", "mapa", aj, comb, e=e,
                   precios=repo.precios_actuales(estacion_id), grafica=grafica)


def _brent_para_grafica(serie: list[dict]) -> list[float | None]:
    brent = mercado.brent_euros()
    return [round(brent[f["fecha"]], 2) if f["fecha"] in brent else None for f in serie]


@app.get("/tendencia")
def tendencia(request: Request, c: str | None = None):
    aj, comb = _elegir(c)
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
    mejor_dia = min(con_datos, key=lambda d: d["media"])["dia"] if len(serie) >= 14 and con_datos else None
    lang = _idioma(request, aj)
    return _pagina(request, "tendencia.html", "tendencia", aj, comb, serie=serie, semana=semana,
                   cambios=cambios, mejor_dia=mejor_dia, prevision=_prevision(aj, comb, lang),
                   brent=_brent_para_grafica(serie))


# --- Ajustes -----------------------------------------------------------------------------

def _validar(form) -> tuple[dict, str | None]:
    """Devuelve los valores y, si algo está mal, la clave del error (en i18n)."""
    v = {k: str(form.get(k, "")).strip().replace(",", ".") for k in config.AJUSTES_POR_DEFECTO
         if k not in ("provincias", "idioma_visto")}
    v["aviso_diario"] = "1" if form.get("aviso_diario") else "0"
    v["avisos_chollo"] = "1" if form.get("avisos_chollo") else "0"
    provincias = [p for p in form.getlist("provincias") if p in config.CODIGOS_PROVINCIA]
    v["provincias"] = ",".join(provincias)
    try:
        if not (-90 <= float(v["lat"]) <= 90 and -180 <= float(v["lon"]) <= 180):
            return v, "err.ubicacion"
        if not 1 <= float(v["radio_km"]) <= 100:
            return v, "err.radio"
        if not 1 <= float(v["litros"]) <= 150:
            return v, "err.litros"
        if not 0 <= float(v["umbral_chollo"]) <= 1:
            return v, "err.umbral"
    except ValueError:
        return v, "err.numero"
    if not re.fullmatch(r"([01]\d|2[0-3]):[0-5]\d", v["hora_aviso"]):
        return v, "err.hora"
    if v["combustible"] not in config.COMBUSTIBLES:
        return v, "err.combustible"
    if not 1 <= len(provincias) <= config.MAX_PROVINCIAS:
        return v, "err.provincias"
    if v["idioma"] not in (*i18n.IDIOMAS, "auto"):
        return v, "err.idioma"
    return v, None


def _pagina_ajustes(request: Request, aj: dict, **datos):
    comb = aj["combustible"] if aj.get("combustible") in config.COMBUSTIBLES else "g95"
    elegidas = aj["provincias"].split(",")
    # Las elegidas, arriba: la lista es corta en pantalla y si no solo se ven las de la A.
    provincias = sorted(config.PROVINCIAS, key=lambda p: p[0] not in elegidas)
    return _pagina(request, "ajustes.html", "ajustes", aj, comb, telegram=avisos.configurado(),
                   provincias=provincias, elegidas=elegidas, idiomas=i18n.IDIOMAS, **datos)


@app.get("/ajustes")
def ver_ajustes(request: Request, guardado: bool = False, prueba: str | None = None):
    return _pagina_ajustes(request, repo.ajustes(), guardado=guardado, prueba=prueba, error=None)


@app.post("/ajustes")
async def guardar_ajustes(request: Request):
    antes = repo.ajustes()
    valores, error = _validar(await request.form())
    if error:
        return _pagina_ajustes(request, {**antes, **valores}, guardado=False, prueba=None, error=error)
    await asyncio.to_thread(repo.guardar_ajustes, valores)
    if valores["provincias"] != antes["provincias"] and not config.SIN_TAREAS:
        asyncio.create_task(asyncio.to_thread(tareas.leer_ahora))     # que no haya que esperar media hora
    return RedirectResponse("/ajustes?guardado=1", status_code=303)


@app.post("/ajustes/prueba")
def probar_telegram():
    try:
        avisos.enviar(i18n.t(avisos.idioma(repo.ajustes()), "tg.prueba"))
        resultado = "ok"
    except Exception:  # noqa: BLE001
        resultado = "error"
    return RedirectResponse(f"/ajustes?prueba={resultado}", status_code=303)


@app.post("/actualizar")
def actualizar():
    tareas.leer_ahora()
    return RedirectResponse("/", status_code=303)


# --- App instalable (PWA) ----------------------------------------------------------------

@app.get("/manifest.webmanifest")
def manifest(request: Request):
    lang = _idioma(request, repo.ajustes())
    return JSONResponse({
        "name": "Pumpcast", "short_name": "Pumpcast", "lang": lang,
        "description": i18n.t(lang, "manifest.descripcion"),
        "start_url": "/", "scope": "/", "display": "standalone",
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
    lang = _idioma(request, repo.ajustes())
    return templates.TemplateResponse(request, "sw.js", {"version": config.VERSION, "lang": lang,
                                                         "aviso": i18n.t(lang, "off.aviso", fecha="{fecha}")},
                                      media_type="text/javascript", headers={"Cache-Control": "no-cache"})


@app.get("/sin-conexion")
def sin_conexion(request: Request):
    aj, comb = _elegir(None)
    return _pagina(request, "sin_conexion.html", "", aj, comb)


# --- Para máquinas -----------------------------------------------------------------------

@app.get("/api/estaciones")
def api_estaciones(c: str | None = None):
    aj, comb = _elegir(c)
    return {"combustible": comb, "estaciones": _para_mapa(repo.cercanas(aj, comb))}


@app.get("/api/resumen")
def api_resumen():
    """Lo de la pantalla de inicio en JSON, para bots y atajos: media, la más barata y el semáforo."""
    aj, comb = _elegir(None)
    lang = avisos.idioma(aj)
    lista = repo.cercanas(aj, comb)
    p = _prevision(aj, comb, lang)
    return {"combustible": i18n.t(lang, "comb." + comb),
            "media": mean(e["precio"] for e in lista) if lista else None,
            "mejor": _para_mapa(lista[:1])[0] if lista else None,
            "prevision": {k: p[k] for k in ("semaforo", "icono", "titulo", "frase", "cambio")} if p["lista"] else None}


@app.get("/api/buscar")
def buscar_direccion(request: Request, q: str = ""):
    """Busca una dirección en OpenStreetMap (Nominatim), solo en España, para poner la casa.
    Devuelve también la provincia, para elegirla sola."""
    q = q.strip()
    if len(q) < 3:
        return {"resultados": []}
    lang = _idioma(request, repo.ajustes())
    url = "https://nominatim.openstreetmap.org/search?" + urllib.parse.urlencode(
        {"q": q, "format": "jsonv2", "limit": 5, "countrycodes": "es", "addressdetails": 1, "accept-language": lang})
    peticion = urllib.request.Request(url, headers={"User-Agent": f"pumpcast/{config.VERSION}"})
    try:
        with urllib.request.urlopen(peticion, timeout=15) as respuesta:
            datos = json.load(respuesta)
    except Exception:  # noqa: BLE001
        raise HTTPException(502, i18n.t(lang, "err.buscador")) from None
    return {"resultados": [{"nombre": d["display_name"], "lat": float(d["lat"]), "lon": float(d["lon"]),
                            "provincia": config.PROVINCIA_POR_ISO.get((d.get("address") or {}).get("ISO3166-2-lvl6"))}
                           for d in datos]}


@app.get("/salud")
def salud():
    """Para Uptime Kuma (palabra clave "ok") y el healthcheck del contenedor."""
    ultima = repo.ultima_lectura()
    estado = "sin-datos"
    if ultima:
        edad = datetime.now(config.TZ) - datetime.fromisoformat(ultima["momento"])
        estado = "ok" if edad < timedelta(hours=3) else "datos-viejos"
    return JSONResponse({"estado": estado, "version": config.VERSION,
                         "ultima_lectura": ultima["momento"] if ultima else None})

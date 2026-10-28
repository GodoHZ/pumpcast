"""Capturas con WebKit (el motor de Safari) a tamaño de iPhone, en castellano y en inglés."""
from playwright.sync_api import sync_playwright

BASE = "http://127.0.0.1:8000"
# El visitante de las capturas ya ha elegido dónde buscar: la Puerta del Sol, 5 km.
UBICACION = "lat=40.4168&lon=-3.7038&radio_km=5&combustible=g95&litros=40&idioma=auto"
PAGINAS = [("inicio", "/"), ("tendencia", "/tendencia"), ("mapa", "/mapa"), ("ajustes", "/ajustes"),
           ("repostajes", "/repostajes")]
# Unos repostajes de ejemplo en el almacenamiento del navegador (de ahí los lee la página).
REPOSTAJES = """localStorage.setItem("pumpcast_repostajes", JSON.stringify([
  {id: "a", fecha: "2026-09-20", litros: 40, precio: 1.689, km: 52300, lleno: true, estacion: "Ballenoil · Madrid"},
  {id: "b", fecha: "2026-10-05", litros: 38.5, precio: 1.702, km: 52900, lleno: true, estacion: "Repsol · Madrid"},
  {id: "c", fecha: "2026-10-21", litros: 41.2, precio: 1.679, km: 53550, lleno: true, estacion: "Ballenoil · Madrid"}]));"""
errores = []

with sync_playwright() as p:
    navegador = p.webkit.launch()
    for lang, locale in (("es", "es-ES"), ("en", "en-GB")):
        for tema in ("light", "dark"):
            ctx = navegador.new_context(viewport={"width": 390, "height": 844}, device_scale_factor=2,
                                        is_mobile=True, has_touch=True, locale=locale, color_scheme=tema,
                                        extra_http_headers={"Accept-Language": locale})
            ctx.add_cookies([{"name": "pumpcast", "value": UBICACION, "url": BASE}])
            ctx.add_init_script(REPOSTAJES)
            pagina = ctx.new_page()
            pagina.on("console", lambda m: errores.append(m.text) if m.type == "error" else None)
            pagina.on("pageerror", lambda e: errores.append(str(e)))
            for nombre, ruta in (PAGINAS if tema == "light" else PAGINAS[:2]):
                pagina.goto(BASE + ruta, wait_until="networkidle")
                pagina.wait_for_timeout(6000 if nombre == "mapa" else 1500)   # que acaben las gráficas y el mapa
                sufijo = "" if tema == "light" else "-oscuro"
                pagina.screenshot(path=f"/out/{nombre}-{lang}{sufijo}.png")
                ancho = pagina.evaluate("document.documentElement.scrollWidth")
                if ancho > 390:
                    errores.append(f"{nombre}-{lang}: scroll horizontal ({ancho}px)")
            ctx.close()
    navegador.close()

# La tarjeta que sale al compartir el enlace (app/static/compartir.png), con la letra y el icono de la app.
TARJETA = """<!doctype html><meta charset="utf-8"><style>
@font-face { font-family: Nunito; src: url(/static/fuentes/nunito.woff2); font-weight: 200 1000; }
body { margin: 0; width: 1200px; height: 630px; overflow: hidden; font-family: Nunito, sans-serif; color: #14202b;
  background: radial-gradient(700px 500px at 0% 0%, rgb(56 189 248 / 45%), transparent 65%),
              radial-gradient(700px 500px at 100% 100%, rgb(165 180 252 / 45%), transparent 65%), #eef4f8;
  display: flex; align-items: center; gap: 56px; padding: 0 90px; box-sizing: border-box; }
img { width: 230px; height: 230px; border-radius: 52px; box-shadow: 0 30px 60px -20px rgb(2 118 181 / 55%); }
div { background: rgb(255 255 255 / 55%); border-radius: 40px; padding: 34px 40px;
  box-shadow: inset 0 1px 0 #fff, inset 0 0 0 1px rgb(255 255 255 / 70%), 0 20px 50px -20px rgb(28 58 88 / 30%); }
h1 { font-size: 92px; font-weight: 900; letter-spacing: -2.5px; margin: 0 0 8px; line-height: 1; }
p { font-size: 34px; line-height: 1.3; margin: 0; font-weight: 600; }
small { display: block; margin-top: 18px; font-size: 26px; color: #0369a1; font-weight: 800; }
</style><img src="/static/iconos/icono-512.png" alt=""><div><h1>Pumpcast</h1>
<p>Las gasolineras más baratas cerca de ti, y si sale a cuenta llenar hoy.</p>
<small>Toda España · precios oficiales cada 30 min</small></div>"""
with sync_playwright() as p:
    navegador = p.webkit.launch()
    pagina = navegador.new_page(viewport={"width": 1200, "height": 630})
    pagina.goto(BASE + "/legal")                          # para que la letra y el icono salgan del mismo sitio
    pagina.set_content(TARJETA.replace("/static", BASE + "/static"), wait_until="networkidle")
    pagina.wait_for_timeout(500)
    pagina.screenshot(path="/out/compartir.png")
    navegador.close()

open("/out/errores.txt", "w").write("\n".join(errores) or "sin errores de consola\n")

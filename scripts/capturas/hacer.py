"""Capturas con WebKit (el motor de Safari) a tamaño de iPhone, en castellano y en inglés."""
from playwright.sync_api import sync_playwright

BASE = "http://127.0.0.1:8000"
PAGINAS = [("inicio", "/"), ("tendencia", "/tendencia"), ("mapa", "/mapa"), ("ajustes", "/ajustes")]
errores = []

with sync_playwright() as p:
    navegador = p.webkit.launch()
    for lang, locale in (("es", "es-ES"), ("en", "en-GB")):
        for tema in ("light", "dark"):
            ctx = navegador.new_context(viewport={"width": 390, "height": 844}, device_scale_factor=2,
                                        is_mobile=True, has_touch=True, locale=locale, color_scheme=tema,
                                        extra_http_headers={"Accept-Language": locale})
            pagina = ctx.new_page()
            pagina.on("console", lambda m: errores.append(m.text) if m.type == "error" else None)
            pagina.on("pageerror", lambda e: errores.append(str(e)))
            for nombre, ruta in (PAGINAS if tema == "light" else PAGINAS[:2]):
                pagina.goto(BASE + ruta, wait_until="networkidle")
                pagina.wait_for_timeout(1500)                  # que acaben las gráficas y el mapa
                sufijo = "" if tema == "light" else "-oscuro"
                pagina.screenshot(path=f"/out/{nombre}-{lang}{sufijo}.png")
                ancho = pagina.evaluate("document.documentElement.scrollWidth")
                if ancho > 390:
                    errores.append(f"{nombre}-{lang}: scroll horizontal ({ancho}px)")
            ctx.close()
    navegador.close()

open("/out/errores.txt", "w").write("\n".join(errores) or "sin errores de consola\n")

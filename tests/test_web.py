import re
from datetime import timedelta

import pytest
from fastapi.testclient import TestClient

from app import config, preferencias, repo
from app.main import app

from conftest import SOL

PREFERENCIAS_BUENAS = {"lat": "40,4168", "lon": "-3,7038", "radio_km": "5", "combustible": "diesel",
                       "litros": "45", "idioma": "auto"}


@pytest.fixture
def cliente():
    with TestClient(app, headers={"Accept-Language": "es-ES,es;q=0.9"}) as c:
        yield c


@pytest.fixture
def cliente_en():
    with TestClient(app, headers={"Accept-Language": "en-GB,en;q=0.9"}) as c:
        yield c


def _ubicar(cliente, **cambios):
    """Un visitante que ya ha elegido dónde buscar (en la Puerta del Sol)."""
    valores = {**PREFERENCIAS_BUENAS, **SOL, "combustible": "g95", "radio_km": "10", **cambios}
    cliente.cookies.set(preferencias.COOKIE, preferencias.para_cookie(valores))
    return cliente


def test_sin_ubicacion_pide_elegirla(cliente, cargada):
    for ruta in ("/", "/mapa", "/tendencia"):
        r = cliente.get(ruta)
        assert r.status_code == 200 and "dinos dónde buscar" in r.text, ruta
    assert cliente.get("/ajustes").status_code == 200
    assert cliente.get("/salud").json()["estado"] == "ok"


def test_paginas_sin_datos(cliente):
    _ubicar(cliente)
    for ruta in ("/", "/mapa", "/tendencia", "/ajustes", "/sin-conexion"):
        assert cliente.get(ruta).status_code == 200, ruta
    assert "Aún no hay precios" in cliente.get("/").text
    assert cliente.get("/salud").json()["estado"] == "sin-datos"


def test_paginas_con_datos(cliente, con_historial, una):
    _ubicar(cliente)
    inicio = cliente.get("/")
    assert inicio.status_code == 200
    assert "La más barata" in inicio.text and "te cuesta" in inicio.text
    for ruta in ("/mapa", "/tendencia", f"/estacion/{una['id']}", "/?c=diesel", "/mapa?c=glp", "/tendencia?c=g98"):
        assert cliente.get(ruta).status_code == 200, ruta
    assert "Esta gasolinera" in cliente.get(f"/estacion/{una['id']}").text
    assert cliente.get("/estacion/1").status_code == 404


def test_cada_visitante_ve_lo_suyo(cliente, cargada):
    """Dos visitantes con radios distintos ven listas distintas, sin pisarse."""
    with TestClient(app, headers={"Accept-Language": "es"}) as otro:
        _ubicar(cliente, radio_km="2")
        _ubicar(otro, radio_km="9")
        cerca, lejos = cliente.get("/").text, otro.get("/").text
    assert "a menos de 2 km" in cerca and "a menos de 9 km" in lejos


def test_estacion_sin_ubicacion(cliente, cargada, una):
    r = cliente.get(f"/estacion/{una['id']}")
    assert r.status_code == 200 and "de tu ubicación" not in r.text


def test_en_ingles(cliente_en, con_historial, una):
    _ubicar(cliente_en)
    inicio = cliente_en.get("/")
    assert '<html lang="en">' in inicio.text
    assert ("Cheapest open within" in inicio.text or "Cheapest within" in inicio.text) and "Petrol 95" in inicio.text
    assert "€" in inicio.text and "La más barata" not in inicio.text
    for ruta in ("/mapa", "/tendencia", "/ajustes", f"/estacion/{una['id']}"):
        r = cliente_en.get(ruta)
        assert r.status_code == 200 and 'lang="en"' in r.text, ruta


def test_el_idioma_de_ajustes_manda(cliente_en, cargada):
    _ubicar(cliente_en, idioma="es")
    assert "La más barata" in cliente_en.get("/").text


def test_combustible_desconocido_usa_el_de_ajustes(cliente, cargada):
    _ubicar(cliente)
    assert cliente.get("/?c=queroseno").status_code == 200


def test_guardar_ajustes_va_a_la_cookie_y_no_a_la_base_de_datos(cliente, cargada):
    antes = repo.ajustes()
    r = cliente.post("/ajustes", data=PREFERENCIAS_BUENAS, follow_redirects=False)
    assert r.status_code == 303 and r.headers["location"] == "/"
    cookie = r.headers["set-cookie"]
    assert cookie.startswith(preferencias.COOKIE + "=") and "httponly" in cookie.lower() and "samesite=lax" in cookie.lower()
    assert repo.ajustes() == antes
    inicio = cliente.get("/")
    assert "a menos de 5 km" in inicio.text and "Diésel" in inicio.text


def test_olvidar_la_ubicacion(cliente, cargada):
    cliente.post("/ajustes", data=PREFERENCIAS_BUENAS)
    assert "a menos de 5 km" in cliente.get("/").text
    r = cliente.post("/ajustes/olvidar", follow_redirects=False)
    assert 'pumpcast=""' in r.headers["set-cookie"] and "Max-Age=0" in r.headers["set-cookie"]
    assert "dinos dónde buscar" in cliente.get("/").text


@pytest.mark.parametrize("cambio, error", [
    ({"radio_km": "500"}, "El radio tiene que estar"),
    ({"lat": "48.85", "lon": "2.35"}, "solo tiene precios de España"),       # París
    ({"lat": "abc"}, "número mal escrito"),
    ({"idioma": "fr"}, "Ese idioma no está disponible"),
    ({"combustible": "queroseno"}, "Ese combustible no existe"),
])
def test_ajustes_con_error_no_se_guardan(cliente, cambio, error):
    r = cliente.post("/ajustes", data={**PREFERENCIAS_BUENAS, **cambio})
    assert r.status_code == 400
    assert error in r.text
    assert preferencias.COOKIE not in r.cookies


def test_una_cookie_trucada_se_ignora(cliente, cargada):
    cliente.cookies.set(preferencias.COOKIE, "lat=40.4&lon=-3.7&radio_km=99999&combustible=g95&litros=40&idioma=auto")
    assert "dinos dónde buscar" in cliente.get("/").text
    cliente.cookies.set(preferencias.COOKIE, '"><script>alert(1)</script>')
    r = cliente.get("/")
    assert r.status_code == 200 and "<script>alert(1)" not in r.text


def test_ajustes_tiene_buscador_y_mapa(cliente):
    texto = cliente.get("/ajustes").text
    assert 'id="buscar"' in texto and 'id="mapa-casa"' in texto
    assert "provincias" not in texto and "Telegram" not in texto


def test_tendencia_dice_que_faltan_datos(cliente, cargada):
    _ubicar(cliente)
    texto = cliente.get("/tendencia").text
    assert "Cargando el histórico" in texto


def test_app_instalable(cliente, cliente_en):
    m = cliente.get("/manifest.webmanifest").json()
    assert m["display"] == "standalone" and m["lang"] == "es"
    for icono in m["icons"]:
        r = cliente.get(icono["src"])
        assert r.status_code == 200 and r.content[:8] == b"\x89PNG\r\n\x1a\n", icono["src"]
    assert cliente_en.get("/manifest.webmanifest").json()["lang"] == "en"
    sw = cliente.get("/sw.js")
    assert sw.headers["content-type"].startswith("text/javascript")
    assert '"/admin"' in sw.text                         # el panel no se guarda para verlo sin conexión
    for recurso in ("/static/vendor/chart.umd.min.js", "/static/vendor/leaflet/leaflet.js",
                    "/static/iconos/apple-touch-icon.png"):
        assert recurso in sw.text or recurso.endswith(".png")
        assert cliente.get(recurso).status_code == 200, recurso


def test_api_con_ubicacion_en_la_url(cliente, cargada):
    r = cliente.get("/api/resumen?lat=40.4168&lon=-3.7038&radio_km=10").json()
    assert r["combustible"] == "Gasolina 95" and r["mejor"]["precio"] <= r["media"]
    assert r["coste"] == round(r["mejor"]["precio"] * 40, 2)
    assert r["prevision"] is None                      # sin histórico todavía
    assert cliente.get("/api/estaciones?lat=40.4168&lon=-3.7038&c=diesel").json()["estaciones"]


def test_api_con_la_cookie(cliente, cargada):
    _ubicar(cliente, litros="50")
    assert cliente.get("/api/resumen").json()["litros"] == 50


def test_api_sin_ubicacion(cliente, cargada):
    assert cliente.get("/api/resumen").status_code == 400
    assert cliente.get("/api/estaciones").status_code == 400
    assert cliente.get("/api/resumen?lat=999&lon=0").status_code == 400


def test_lo_que_se_quito_ya_no_existe(cliente):
    """Lo que dejaba a cualquiera tocar el servidor desde la web pública."""
    assert cliente.post("/actualizar").status_code in (404, 405)
    assert cliente.post("/ajustes/prueba").status_code in (404, 405)
    assert cliente.get("/api/buscar?q=madrid").status_code == 404


# --- Usar dónde estoy ----------------------------------------------------------------------

def test_sin_gps_no_se_pide_la_ubicacion(cliente, cargada):
    _ubicar(cliente)
    assert "gps.js" not in cliente.get("/").text
    assert cliente.post("/ubicacion", data={"lat": "41.3874", "lon": "2.1686"}).status_code == 409


def test_con_gps_cada_pagina_pide_la_ubicacion(cliente, cargada):
    _ubicar(cliente, gps="1")
    for ruta in ("/", "/mapa", "/tendencia"):
        texto = cliente.get(ruta).text
        assert '<script src="/static/gps.js' in texto and 'id="gps-estado"' in texto, ruta
    assert "gps.js" not in cliente.get("/ajustes").text
    assert cliente.get("/static/gps.js").status_code == 200


def test_la_casilla_del_gps_se_guarda(cliente, cargada):
    cliente.post("/ajustes", data={**PREFERENCIAS_BUENAS, "gps": "1"})
    assert "gps.js" in cliente.get("/").text
    assert 'id="gps" checked' in cliente.get("/ajustes").text
    cliente.post("/ajustes", data=PREFERENCIAS_BUENAS)                 # casilla sin marcar: no llega
    assert "gps.js" not in cliente.get("/").text


def test_moverse_cambia_la_cookie_redondeada(cliente, cargada):
    _ubicar(cliente, gps="1")
    r = cliente.post("/ubicacion", data={"lat": "40.4530123", "lon": "-3.6883456"})     # ~5 km del Sol
    assert r.json() == {"cambiada": True}
    guardada = preferencias.leer_texto(r.cookies[preferencias.COOKIE].strip('"'))
    assert guardada["lat"] == "40.45300" and guardada["lon"] == "-3.68800"            # ~100 m, no el portal
    assert guardada["gps"] == "1" and guardada["radio_km"] == "10"                    # lo demás, igual


def test_moverse_poco_no_recarga(cliente, cargada):
    _ubicar(cliente, gps="1")
    r = cliente.post("/ubicacion", data={"lat": float(SOL["lat"]) + 0.003, "lon": SOL["lon"]})   # ~300 m
    assert r.json() == {"cambiada": False} and preferencias.COOKIE not in r.cookies


@pytest.mark.parametrize("datos, error", [
    ({"lat": "48.85", "lon": "2.35"}, "err.fuera"),                   # de viaje en París
    ({"lat": "abc", "lon": "2"}, "err.numero"),
    ({}, "err.numero"),
])
def test_una_posicion_mala_no_cambia_nada(cliente, cargada, datos, error):
    _ubicar(cliente, gps="1")
    r = cliente.post("/ubicacion", data=datos)
    assert r.status_code == 400 and r.json()["error"] == error and preferencias.COOKIE not in r.cookies


def test_la_ubicacion_no_se_acepta_desde_otra_web(cliente, cargada):
    _ubicar(cliente, gps="1")
    r = cliente.post("/ubicacion", data={"lat": "41.38", "lon": "2.16"}, headers={"Origin": "https://malvada.example"})
    assert r.status_code == 403


def test_sin_emojis_en_la_web(cliente, con_historial, una):
    """Iconos dibujados en vez de emojis, que cambian de un móvil a otro (en Telegram sí se usan)."""
    import re
    emoji = re.compile("[\U0001F000-\U0001FAFF☀-➿⬀-⯿]")
    _ubicar(cliente, gps="1")
    for ruta in ("/", "/mapa", "/tendencia", "/ajustes", f"/estacion/{una['id']}"):
        texto = cliente.get(ruta).text
        assert not emoji.search(texto), (ruta, emoji.findall(texto))
        assert texto.count('class="icono"') >= 4, ruta                  # la barra de abajo


# --- Lo legal y los errores ----------------------------------------------------------------

def test_aviso_legal(cliente, cliente_en, cargada, monkeypatch):
    texto = cliente.get("/legal").text
    for frase in ("Ministerio para la Transición Ecológica", "Ley 37/2007", "FRED", "Banco Central Europeo",
                  "OpenStreetMap", "art. 22.2 de la LSSI", "aepd.es", "github.com/GodoHZ/pumpcast/issues"):
        assert frase in texto, frase
    assert "Spanish Law 37/2007" in cliente_en.get("/legal").text
    monkeypatch.setattr(config, "CONTACTO", "hola@example.com")
    monkeypatch.setattr(config, "TITULAR", "Fulano")
    texto = cliente.get("/legal").text
    assert 'href="mailto:hola@example.com"' in texto and "de Fulano" in texto


def test_todas_las_paginas_citan_la_fuente(cliente, cargada):
    _ubicar(cliente)
    for ruta in ("/", "/mapa", "/tendencia", "/ajustes"):
        texto = cliente.get(ruta).text
        assert "Precios: Ministerio para la Transición Ecológica" in texto and 'href="/legal"' in texto, ruta


def test_pagina_que_no_existe(cliente):
    r = cliente.get("/no-existe")
    assert r.status_code == 404 and "Esta página no existe" in r.text and 'class="barra"' in r.text
    assert cliente.get("/estacion/1").status_code == 404
    assert cliente.get("/api/no-existe").json() == {"detail": "Not Found"}      # las máquinas, JSON


def test_la_grafica_dice_hasta_cuando_hay_brent(cliente, con_historial, monkeypatch):
    """El Brent se publica con retraso: la gráfica lo explica en vez de cortarse sin más."""
    from app import main
    momento, _ = con_historial
    hace_una_semana = (momento - timedelta(days=6)).date().isoformat()
    monkeypatch.setattr(main.mercado, "brent_euros", lambda: {hace_una_semana: 100.0})
    texto = _ubicar(cliente).get("/tendencia").text
    assert "El Brent llega hasta el" in texto and "brent_pendiente" in texto


def test_el_gas_natural_va_por_kilos(cliente, cargada):
    _ubicar(cliente)
    assert "Llenar 45 L" in cliente.get("/").text
    gnc = cliente.get("/?c=gnc").text
    assert "GNC" in gnc and "Llenar 45 kg" in gnc


def test_ordenar_por_cercania_se_recuerda(cliente, cargada):
    _ubicar(cliente)
    por_precio = cliente.get("/").text
    assert "Más baratas" in por_precio and "La más cercana" in por_precio
    r = cliente.get("/?orden=distancia")
    assert preferencias.leer_texto(r.cookies.get(preferencias.COOKIE).strip('"'))["orden"] == "distancia"
    lista = r.text.split('class="lista"')[1]
    distancias = [float(x.replace(",", ".")) for x in re.findall(r"· ([\d,]+) km ·", lista)]
    assert len(distancias) > 2 and distancias == sorted(distancias)


def test_como_llegar_pregunta_la_app(cliente, cargada, una):
    _ubicar(cliente)
    for texto in (cliente.get("/").text, cliente.get(f"/estacion/{una['id']}").text):
        assert 'data-ir="' in texto and "google.com/maps/dir" in texto           # sin JavaScript, Google Maps
        assert 'id="elegir-mapa"' in texto and "waze.com/ul" in texto and "maps.apple.com" in texto
    assert "como_llegar" in cliente.get("/mapa").text


def test_la_app_en_catalan(cliente, cargada):
    _ubicar(cliente, idioma="ca")
    assert "La més barata" in cliente.get("/").text
    assert "Català" in cliente.get("/ajustes").text
    legal = cliente.get("/legal").text
    assert "en castellà" in legal and "Quién está detrás" in legal


def test_favoritas(cliente, cargada, una):
    _ubicar(cliente)
    ficha = f"/estacion/{una['id']}"
    assert "Favorita" in cliente.get(ficha).text
    r = cliente.post(f"/favorita/{una['id']}", headers={"Referer": f"http://testserver{ficha}?c=g95"},
                     follow_redirects=False)
    assert r.status_code == 303 and r.headers["location"] == f"{ficha}?c=g95"
    assert "Tus favoritas" in cliente.get("/").text and "Quitar de favoritas" in cliente.get(ficha).text
    cliente.post(f"/favorita/{una['id']}")
    assert "Tus favoritas" not in cliente.get("/").text
    assert cliente.post("/favorita/1").status_code == 404
    r = cliente.post(f"/favorita/{una['id']}", headers={"Referer": "https://otra.web/x"}, follow_redirects=False)
    assert r.status_code == 403                              # desde otra web, ni se toca


def test_ordenar_por_lo_que_compensa(cliente, cargada):
    _ubicar(cliente, consumo="8")
    texto = cliente.get("/?orden=compensa").text
    assert "con el viaje" in texto and "8 L/100 km" in texto


def test_el_horario_sale_en_la_ficha(cliente, cargada, una):
    _ubicar(cliente)
    texto = cliente.get(f"/estacion/{una['id']}").text
    assert "Horario publicado" in texto or not una.get("horario")


def test_tarjeta_para_compartir(cliente, cargada):
    texto = cliente.get("/legal").text
    assert 'property="og:image" content="http://testserver/static/compartir.png?v=' in texto
    assert 'name="twitter:image"' in texto and 'property="og:locale" content="es_ES"' in texto
    assert cliente.get("/static/compartir.png").status_code == 200


def test_salud_avisa_si_el_brent_no_llega(cliente, cargada, monkeypatch):
    from app import main
    monkeypatch.setattr(main.mercado, "ultimo_brent", lambda: "2020-01-01")
    assert cliente.get("/salud").json()["estado"] == "brent-viejo"
    monkeypatch.setattr(main.mercado, "ultimo_brent", lambda: None)            # recién instalada
    assert cliente.get("/salud").json()["estado"] == "ok"


def test_el_aviso_legal_cuenta_lo_que_hace_falta(cliente):
    texto = cliente.get("/legal").text
    for frase in ("6.1.b", "6.1.a", "6.1.f", "Marco de", "OpenFreeMap", "pumpcast_fav", "MapLibre"):
        assert frase in texto, frase


def test_elegir_el_tema(cliente, cargada):
    _ubicar(cliente)
    assert "data-theme" not in cliente.get("/").text.split(">", 2)[1]       # automático: el del móvil
    _ubicar(cliente, tema="oscuro")
    assert '<html lang="es" data-theme="dark">' in cliente.get("/").text
    _ubicar(cliente, tema="claro")
    assert 'data-theme="light"' in cliente.get("/ajustes").text
    _ubicar(cliente, tema="raro")
    assert "data-theme" not in cliente.get("/").text.split(">", 2)[1]


def test_favorita_y_horario_desde_cerca_y_el_mapa(cliente, cargada):
    _ubicar(cliente)
    assert 'action="/favorita/' in cliente.get("/").text
    mapa = cliente.get("/mapa").text
    assert "const favoritas = new Set([])" in mapa and '"horario":' in mapa


def test_ajustes_se_guardan_solos(cliente, cargada):
    _ubicar(cliente)
    datos = {**PREFERENCIAS_BUENAS, **SOL, "combustible": "g95", "tema": "oscuro"}
    r = cliente.post("/ajustes", data=datos, headers={"Accept": "application/json"})
    assert r.json() == {"ok": True} and "tema=oscuro" in r.headers["set-cookie"]
    r = cliente.post("/ajustes", data={**datos, "radio_km": "500"}, headers={"Accept": "application/json"})
    assert r.status_code == 400 and "radio" in r.json()["error"]
    assert "data-auto" in cliente.get("/ajustes").text


def test_la_destacada_sigue_el_orden(cliente, cargada):
    _ubicar(cliente)
    barata = cliente.get("/?orden=precio").text
    cercana = cliente.get("/?orden=distancia").text
    rentable = cliente.get("/?orden=compensa").text
    assert "La más barata" in barata and "La más cercana" in cercana and "La más rentable" in rentable
    assert "Contando el viaje" in rentable and "Más rentables" in rentable
    assert barata.index('class="segmentos"') < barata.index('class="tarjeta destacada"')


def test_aviso_para_instalarla(cliente, cargada):
    assert 'id="instalar"' in cliente.get("/").text and "data-auto" not in cliente.get("/").text.split('id="instalar"')[1][:200]
    _ubicar(cliente)
    texto = cliente.get("/").text
    trozo = texto.split('id="instalar"')[1][:300]
    assert "data-auto" in trozo and "Añadir a pantalla de inicio" in texto
    assert 'id="instalar-abrir"' in cliente.get("/ajustes").text


def test_las_paginas_van_comprimidas(cliente, cargada):
    _ubicar(cliente)
    r = cliente.get("/", headers={"Accept-Encoding": "gzip"})
    assert r.headers.get("content-encoding") == "gzip" and "content-security-policy" in r.headers

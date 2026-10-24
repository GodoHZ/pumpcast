import pytest
from fastapi.testclient import TestClient

from app import repo
from app.main import app

AJUSTES_BUENOS = {"lat": "40,42", "lon": "-3,70", "radio_km": "15", "combustible": "diesel", "litros": "45",
                  "umbral_chollo": "0,04", "hora_aviso": "07:45", "aviso_diario": "1",
                  "provincias": ["28", "45"], "idioma": "auto"}


@pytest.fixture
def cliente():
    with TestClient(app, headers={"Accept-Language": "es-ES,es;q=0.9"}) as c:
        yield c


@pytest.fixture
def cliente_en():
    with TestClient(app, headers={"Accept-Language": "en-GB,en;q=0.9"}) as c:
        yield c


def test_paginas_sin_datos(cliente):
    for ruta in ("/", "/mapa", "/tendencia", "/ajustes", "/sin-conexion"):
        assert cliente.get(ruta).status_code == 200, ruta
    assert "Aún no hay precios" in cliente.get("/").text
    assert cliente.get("/salud").json()["estado"] == "sin-datos"


def test_primera_vez_pide_la_provincia(cliente):
    repo.guardar_ajustes({"provincias": ""})
    assert "elige tu provincia" in cliente.get("/").text


def test_paginas_con_datos(cliente, con_historial, una):
    inicio = cliente.get("/")
    assert inicio.status_code == 200
    assert "La más barata" in inicio.text
    for ruta in ("/mapa", "/tendencia", f"/estacion/{una['id']}", "/?c=diesel", "/mapa?c=glp", "/tendencia?c=g98"):
        assert cliente.get(ruta).status_code == 200, ruta
    assert "Esta gasolinera" in cliente.get(f"/estacion/{una['id']}").text
    assert cliente.get("/estacion/1").status_code == 404
    assert cliente.get("/salud").json()["estado"] == "ok"
    assert cliente.get("/api/estaciones").json()["estaciones"]


def test_en_ingles(cliente_en, con_historial, una):
    inicio = cliente_en.get("/")
    assert '<html lang="en">' in inicio.text
    assert "Cheapest within" in inicio.text and "Petrol 95" in inicio.text
    assert "€" in inicio.text and "La más barata" not in inicio.text
    for ruta in ("/mapa", "/tendencia", "/ajustes", f"/estacion/{una['id']}"):
        r = cliente_en.get(ruta)
        assert r.status_code == 200 and 'lang="en"' in r.text, ruta


def test_el_idioma_de_ajustes_manda(cliente_en, cargada):
    repo.guardar_ajustes({"idioma": "es"})
    assert "La más barata" in cliente_en.get("/").text


def test_se_recuerda_el_idioma_del_navegador_para_los_avisos(cliente_en):
    cliente_en.get("/")
    assert repo.ajustes()["idioma_visto"] == "en"


def test_combustible_desconocido_usa_el_de_ajustes(cliente, cargada):
    assert cliente.get("/?c=queroseno").status_code == 200


def test_guardar_ajustes(cliente):
    r = cliente.post("/ajustes", data=AJUSTES_BUENOS, follow_redirects=False)
    assert r.status_code == 303
    aj = repo.ajustes()
    assert aj["lat"] == "40.42" and aj["radio_km"] == "15" and aj["combustible"] == "diesel"
    assert aj["umbral_chollo"] == "0.04" and aj["provincias"] == "28,45"
    assert aj["aviso_diario"] == "1" and aj["avisos_chollo"] == "0"


@pytest.mark.parametrize("cambio, error", [
    ({"radio_km": "500"}, "El radio tiene que estar"),
    ({"provincias": []}, "Elige entre 1 y 4 provincias"),
    ({"provincias": ["01", "02", "03", "04", "05"]}, "Elige entre 1 y 4 provincias"),
    ({"hora_aviso": "8h"}, "La hora del aviso va como"),
    ({"idioma": "fr"}, "Ese idioma no está disponible"),
])
def test_ajustes_con_error_no_se_guardan(cliente, cambio, error):
    r = cliente.post("/ajustes", data={**AJUSTES_BUENOS, **cambio})
    assert r.status_code == 200
    assert error in r.text
    assert repo.ajustes()["radio_km"] == "10"


def test_buscar_direccion_corta_no_llama_a_nadie(cliente):
    assert cliente.get("/api/buscar?q=al").json() == {"resultados": []}


def test_ajustes_tiene_buscador_mapa_y_provincias(cliente):
    texto = cliente.get("/ajustes").text
    assert 'id="buscar"' in texto and 'id="mapa-casa"' in texto
    assert '<option value="28" selected>Madrid</option>' in texto


def test_tendencia_dice_que_faltan_datos(cliente, cargada):
    assert "Cargando el histórico" in cliente.get("/tendencia").text


def test_app_instalable(cliente, cliente_en):
    m = cliente.get("/manifest.webmanifest").json()
    assert m["display"] == "standalone" and m["lang"] == "es"
    for icono in m["icons"]:
        r = cliente.get(icono["src"])
        assert r.status_code == 200 and r.content[:8] == b"\x89PNG\r\n\x1a\n", icono["src"]
    assert cliente_en.get("/manifest.webmanifest").json()["lang"] == "en"
    sw = cliente.get("/sw.js")
    assert sw.headers["content-type"].startswith("text/javascript")
    for recurso in ("/static/vendor/chart.umd.min.js", "/static/vendor/leaflet/leaflet.js",
                    "/static/iconos/apple-touch-icon.png"):
        assert recurso in sw.text or recurso.endswith(".png")
        assert cliente.get(recurso).status_code == 200, recurso


def test_api_resumen(cliente, cargada):
    r = cliente.get("/api/resumen").json()
    assert r["combustible"] == "Gasolina 95" and r["mejor"]["precio"] <= r["media"]
    assert r["prevision"] is None                      # sin histórico todavía


def test_prueba_de_telegram_sin_configurar(cliente):
    r = cliente.post("/ajustes/prueba", follow_redirects=False)
    assert r.headers["location"] == "/ajustes?prueba=error"

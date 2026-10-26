"""Las cerraduras de la web pública y del panel de administración."""
import re
import time

import pytest
from fastapi.testclient import TestClient

from app import config, preferencias, repo, seguridad
from app.main import app

CLAVE = "una-clave-larga-de-pruebas"
CASA_SECRETA = {"lat": "40.41234", "lon": "-3.70987"}       # la del dueño: no debe salir nunca en público


@pytest.fixture
def cliente():
    with TestClient(app, headers={"Accept-Language": "es"}) as c:
        yield c


@pytest.fixture
def con_clave(monkeypatch):
    monkeypatch.setattr(config, "ADMIN_PASSWORD_HASH", seguridad.hash_clave(CLAVE))


def _codigo(secreto, desfase=0):
    return seguridad.codigo_totp(secreto, int(time.time() // seguridad.PASO) + desfase)


def _dar_de_alta(cliente) -> str:
    """Entra por primera vez, da de alta la verificación en dos pasos y devuelve el secreto."""
    r = cliente.post("/admin/entrar", data={"clave": CLAVE})
    assert r.status_code == 200 and "Verificación en dos pasos" in r.text
    secreto = re.search(r"<code>([A-Z2-7]+)</code>", r.text).group(1)
    assert f"secret={secreto}" in r.text
    r = cliente.post("/admin/alta", data={"codigo": _codigo(secreto)}, follow_redirects=False)
    assert r.status_code == 303 and r.headers["location"] == "/admin"
    return secreto


# --- Contraseña y TOTP -------------------------------------------------------------------

def test_hash_de_la_clave():
    guardado = seguridad.hash_clave(CLAVE)
    assert guardado.startswith("scrypt:") and "$" not in guardado and CLAVE not in guardado
    assert seguridad.comprobar_clave(CLAVE, guardado)
    assert not seguridad.comprobar_clave(CLAVE + "x", guardado)
    assert not seguridad.comprobar_clave(CLAVE, "basura")
    assert seguridad.hash_clave(CLAVE) != guardado                     # sal distinta cada vez


def test_totp_rfc_6238():
    """El vector de prueba de la RFC 6238 (SHA-1, T = 59 s → 94287082, últimas 6 cifras)."""
    secreto = "GEZDGNBVGY3TQOJQGEZDGNBVGY3TQOJQ"                       # "12345678901234567890"
    assert seguridad.codigo_totp(secreto, 59 // 30) == "287082"
    assert seguridad.comprobar_totp(secreto, "287 082", ahora=59)
    assert not seguridad.comprobar_totp(secreto, "287082", ahora=59)   # el mismo código no vale dos veces
    assert not seguridad.comprobar_totp(secreto, "123456", ahora=10_000)
    assert not seguridad.comprobar_totp(secreto, "12345", ahora=10_000)


# --- El panel ----------------------------------------------------------------------------

def test_sin_clave_configurada_el_panel_no_existe(cliente):
    assert cliente.get("/admin").status_code == 404
    assert cliente.post("/admin/entrar", data={"clave": "x"}).status_code == 404


def test_desde_internet_el_panel_no_existe(cliente, con_clave):
    """Lo que entra por Cloudflare lleva CF-Connecting-IP: para eso el panel no existe."""
    cf = {"CF-Connecting-IP": "203.0.113.7", "X-Forwarded-Proto": "https"}
    assert cliente.get("/admin", headers=cf).status_code == 404
    assert cliente.post("/admin/entrar", data={"clave": CLAVE}, headers=cf).status_code == 404
    _dar_de_alta(cliente)                                              # con sesión desde casa...
    assert cliente.get("/admin", headers=cf).status_code == 404        # ...tampoco por Cloudflare
    assert cliente.post("/admin/prueba", headers=cf).status_code == 404
    with TestClient(app, base_url="https://testserver") as seguro:                # como llega por el túnel
        for ruta in ("/admin/", "/admin/entrar", "/ADMIN", "/admin/no-existe"):   # ni 405 ni 307
            assert seguro.get(ruta, headers=cf, follow_redirects=False).status_code == 404, ruta


def test_alta_y_entrada_con_dos_pasos(cliente, con_clave):
    assert "Contraseña" in cliente.get("/admin").text
    secreto = _dar_de_alta(cliente)
    assert repo.secreto("totp") == secreto
    panel = cliente.get("/admin")
    assert "Avisos por Telegram" in panel.text and panel.headers["cache-control"] == "no-store"
    cliente.post("/admin/salir")
    assert "Código de 6 cifras" in cliente.get("/admin").text          # ya pide el código
    sin_codigo = cliente.post("/admin/entrar", data={"clave": CLAVE})
    assert sin_codigo.status_code == 401
    r = cliente.post("/admin/entrar", data={"clave": CLAVE, "codigo": _codigo(secreto, 1)}, follow_redirects=False)
    assert r.status_code == 303
    cookie = r.headers["set-cookie"].lower()
    assert "httponly" in cookie and "samesite=strict" in cookie and "path=/admin" in cookie
    assert "Avisos por Telegram" in cliente.get("/admin").text


def test_clave_mal(cliente, con_clave):
    r = cliente.post("/admin/entrar", data={"clave": "no-es-esta"})
    assert r.status_code == 401 and "incorrectos" in r.text
    assert repo.secreto("totp") is None


def test_codigo_mal_al_dar_de_alta(cliente, con_clave):
    cliente.post("/admin/entrar", data={"clave": CLAVE})
    r = cliente.post("/admin/alta", data={"codigo": "000000"})
    assert r.status_code == 401 and repo.secreto("totp") is None


def test_no_se_puede_dar_de_alta_sin_la_clave(cliente, con_clave):
    r = cliente.post("/admin/alta", data={"codigo": "123456"}, follow_redirects=False)
    assert r.status_code == 303 and repo.secreto("totp") is None


def test_bloqueo_tras_varios_fallos(cliente, con_clave):
    for _ in range(seguridad.MAX_FALLOS_POR_IP):
        assert cliente.post("/admin/entrar", data={"clave": "mal"}).status_code == 401
    r = cliente.post("/admin/entrar", data={"clave": CLAVE})            # ni con la buena
    assert r.status_code == 429 and "Demasiados intentos" in r.text


def test_sin_sesion_no_se_toca_nada(cliente, con_clave):
    for ruta in ("/admin", "/admin/prueba", "/admin/actualizar"):
        r = cliente.post(ruta, data={**CASA_SECRETA}, follow_redirects=False)
        assert r.status_code == 303 and r.headers["location"] == "/admin", ruta
    assert repo.ajustes()["lat"] != CASA_SECRETA["lat"]


def test_una_sesion_inventada_no_vale(cliente, con_clave):
    cliente.cookies.set(seguridad.COOKIE_ADMIN, "inventada", path="/admin")
    assert "Contraseña" in cliente.get("/admin").text


def test_guardar_los_avisos(cliente, con_clave):
    _dar_de_alta(cliente)
    datos = {**CASA_SECRETA, "radio_km": "7", "combustible": "diesel", "litros": "50", "hora_aviso": "07:15",
             "aviso_diario": "1", "umbral_chollo": "0,04", "idioma": "en"}
    r = cliente.post("/admin", data=datos, follow_redirects=False)
    assert r.status_code == 303
    aj = repo.ajustes()
    assert aj["lat"] == CASA_SECRETA["lat"] and aj["hora_aviso"] == "07:15" and aj["idioma"] == "en"
    assert aj["aviso_diario"] == "1" and aj["avisos_chollo"] == "0" and aj["umbral_chollo"] == "0.04"
    assert cliente.post("/admin", data={**datos, "hora_aviso": "8h"}).status_code == 400


# --- La web pública ----------------------------------------------------------------------

def test_la_casa_del_dueno_no_sale_en_publico(cliente, cargada):
    repo.guardar_ajustes(CASA_SECRETA)
    visitante = {"lat": "40.4168", "lon": "-3.7038", "radio_km": "10", "combustible": "g95", "litros": "40",
                 "idioma": "auto"}
    for con_cookie in (False, True):
        if con_cookie:
            cliente.cookies.set(preferencias.COOKIE, preferencias.para_cookie(visitante))
        for ruta in ("/", "/mapa", "/tendencia", "/ajustes", "/manifest.webmanifest", "/sw.js",
                     "/api/resumen?lat=40.4&lon=-3.7", "/api/estaciones?lat=40.4&lon=-3.7"):
            texto = cliente.get(ruta).text
            assert CASA_SECRETA["lat"] not in texto and CASA_SECRETA["lon"] not in texto, ruta


def test_cabeceras_de_seguridad(cliente):
    r = cliente.get("/ajustes")
    csp = r.headers["content-security-policy"]
    nonce = re.search(r"'nonce-([^']+)'", csp).group(1)
    assert f'<script nonce="{nonce}">' in r.text
    assert "frame-ancestors 'none'" in csp and "object-src 'none'" in csp and "unsafe-eval" not in csp
    assert "script-src 'self' 'nonce-" in csp
    assert r.headers["x-frame-options"] == "DENY"
    assert r.headers["x-content-type-options"] == "nosniff"
    assert r.headers["referrer-policy"] == "strict-origin-when-cross-origin"
    assert nonce not in cliente.get("/ajustes").headers["content-security-policy"]    # uno nuevo cada vez


def test_todos_los_scripts_en_linea_llevan_nonce(cliente, cargada):
    cliente.cookies.set(preferencias.COOKIE, "lat=40.4168&lon=-3.7038&radio_km=10&combustible=g95&litros=40&idioma=auto")
    for ruta in ("/", "/mapa", "/tendencia", "/ajustes"):
        texto = cliente.get(ruta).text
        assert not re.search(r"<script(?![^>]*\b(src|nonce)=)[^>]*>", texto), ruta


def test_formularios_de_otra_web(cliente):
    datos = {"lat": "40.4", "lon": "-3.7", "radio_km": "5", "combustible": "g95", "litros": "40", "idioma": "auto"}
    assert cliente.post("/ajustes", data=datos, headers={"Origin": "https://malvada.example"}).status_code == 403
    assert cliente.post("/ajustes", data=datos, headers={"Referer": "https://malvada.example/x"}).status_code == 403
    assert cliente.post("/ajustes", data=datos, headers={"Origin": "null"}).status_code == 403
    r = cliente.post("/ajustes", data=datos, headers={"Origin": "http://testserver"}, follow_redirects=False)
    assert r.status_code == 303


def test_desde_internet_siempre_https(cliente):
    cf = {"CF-Connecting-IP": "203.0.113.7"}
    r = cliente.get("/tendencia?c=diesel", headers=cf, follow_redirects=False)
    assert r.status_code == 301 and r.headers["location"] == "https://testserver/tendencia?c=diesel"
    assert cliente.get("/tendencia", follow_redirects=False).status_code == 200      # desde casa, como esté
    with TestClient(app, base_url="https://testserver") as seguro:
        r = seguro.get("/", headers=cf)
        assert r.status_code == 200 and r.headers["strict-transport-security"].startswith("max-age=")


def test_limite_de_peticiones(cliente, monkeypatch):
    monkeypatch.setattr(seguridad, "PETICIONES_POR_MINUTO", 3)
    assert [cliente.get("/legal").status_code for _ in range(4)] == [200, 200, 200, 429]
    r = cliente.get("/legal", headers={"Accept-Language": "ca"})
    assert "Espera un minut" in r.text and r.headers["retry-after"] == "60"
    for ruta in ("/static/estilo.css", "/salud", "/sw.js", "/manifest.webmanifest"):
        assert cliente.get(ruta).status_code == 200, ruta                 # lo que el navegador pide solo no cuenta
    otra_ip = {"CF-Connecting-IP": "198.51.100.1", "X-Forwarded-Proto": "https"}
    assert cliente.get("/legal", headers=otra_ip).status_code == 200      # cada IP lleva su cuenta


def test_comandos_de_terminal(monkeypatch, capsys):
    import io
    monkeypatch.setattr("sys.stdin", io.StringIO(CLAVE + "\n"))
    assert seguridad._main(["hash"]) == 0
    assert seguridad.comprobar_clave(CLAVE, capsys.readouterr().out.strip())
    repo.guardar_secreto("totp", "ABC")
    assert seguridad._main(["quitar-2fa"]) == 0 and repo.secreto("totp") is None

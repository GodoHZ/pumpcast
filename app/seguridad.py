"""Lo que hace falta para poner Pumpcast en Internet sin sustos.

- Cabeceras de seguridad en cada respuesta, con una política de contenido (CSP) que solo deja
  ejecutar los scripts de la propia app (los de las páginas llevan un «nonce» distinto cada vez).
- Un límite de peticiones por IP, para que nadie la tumbe a base de recargar.
- Los formularios solo se aceptan si vienen de la propia web (contra CSRF).
- El panel de administración: contraseña (guardada como hash scrypt) y verificación en dos
  pasos (TOTP, el código de 6 cifras de Google Authenticator, Aegis, 1Password...). Además, no
  existe para lo que entra por Cloudflare: solo se llega desde la red de casa o una VPN.

Desde la terminal del contenedor:
    python -m app.seguridad hash         pide una contraseña y escribe su hash (ADMIN_PASSWORD_HASH)
    python -m app.seguridad quitar-2fa   borra la verificación en dos pasos (se vuelve a dar de alta al entrar)
"""
from __future__ import annotations

import base64
import hashlib
import hmac
import secrets
import struct
import sys
import time
import urllib.parse
from collections import defaultdict, deque

from fastapi import Request
from fastapi.responses import JSONResponse, PlainTextResponse, RedirectResponse

from . import config, repo

# --- Quién es quién ----------------------------------------------------------------------

def ip(request: Request) -> str:
    """La IP del visitante. Cloudflare la pone en CF-Connecting-IP; si no, la que dejó el proxy."""
    return request.headers.get("cf-connecting-ip") or (request.client.host if request.client else "?")


def desde_internet(request: Request) -> bool:
    """Si la petición ha entrado por Cloudflare. Cloudflare siempre pone esta cabecera y quien
    visita no puede quitarla; desde la red de casa (o Tailscale) no llega."""
    return "cf-connecting-ip" in request.headers


def es_https(request: Request) -> bool:
    return request.url.scheme == "https"


# --- Contraseña --------------------------------------------------------------------------
# Formato: scrypt:<sal en hex>:<hash en hex>. Sin «$», que docker compose lo interpretaría.

_SCRYPT = {"n": 2 ** 14, "r": 8, "p": 1, "dklen": 32}


def hash_clave(clave: str) -> str:
    sal = secrets.token_bytes(16)
    return f"scrypt:{sal.hex()}:{hashlib.scrypt(clave.encode(), salt=sal, **_SCRYPT).hex()}"


def comprobar_clave(clave: str, guardado: str) -> bool:
    try:
        tipo, sal, esperado = guardado.split(":")
        if tipo != "scrypt":
            return False
        calculado = hashlib.scrypt(clave.encode(), salt=bytes.fromhex(sal), **_SCRYPT).hex()
    except ValueError:
        return False
    return hmac.compare_digest(calculado, esperado)


# --- Verificación en dos pasos (TOTP, RFC 6238) ------------------------------------------

PASO = 30


def nuevo_secreto_totp() -> str:
    return base64.b32encode(secrets.token_bytes(20)).decode()


def codigo_totp(secreto: str, paso: int) -> str:
    clave = base64.b32decode(secreto)
    resumen = hmac.new(clave, struct.pack(">Q", paso), hashlib.sha1).digest()
    desplazamiento = resumen[-1] & 0x0F
    numero = struct.unpack(">I", resumen[desplazamiento:desplazamiento + 4])[0] & 0x7FFFFFFF
    return f"{numero % 1_000_000:06d}"


_ultimo_paso_usado = -1


def comprobar_totp(secreto: str, codigo: str, ahora: float | None = None) -> bool:
    """Acepta el código de ahora y los de 30 s antes o después (relojes que no van finos), pero
    cada código solo sirve una vez: quien lo vea por encima del hombro no puede reutilizarlo."""
    global _ultimo_paso_usado
    codigo = "".join(c for c in codigo if c.isdigit())
    if len(codigo) != 6:
        return False
    actual = int((time.time() if ahora is None else ahora) // PASO)
    for paso in (actual - 1, actual, actual + 1):
        if paso > _ultimo_paso_usado and hmac.compare_digest(codigo_totp(secreto, paso), codigo):
            _ultimo_paso_usado = paso
            return True
    return False


def enlace_totp(secreto: str) -> str:
    """El otpauth:// que entienden las apps de autenticación (y lo que lleva el código QR)."""
    return (f"otpauth://totp/Pumpcast:admin?secret={secreto}&issuer=Pumpcast"
            f"&algorithm=SHA1&digits=6&period={PASO}")


def secreto_totp() -> str | None:
    return repo.secreto("totp")


# --- Sesiones del panel ------------------------------------------------------------------
# En memoria: si el contenedor se reinicia, hay que volver a entrar. Así no hay nada que robar
# del disco.

COOKIE_ADMIN = "pumpcast_admin"
COOKIE_ALTA = "pumpcast_alta"
HORAS_DE_SESION = 8
MINUTOS_DE_ALTA = 10

_sesiones: dict[str, float] = {}
_altas: dict[str, tuple[str, float]] = {}       # ficha -> (secreto TOTP por confirmar, caduca)


def _limpiar(diccionario: dict, caduca) -> None:
    ahora = time.time()
    for k in [k for k, v in diccionario.items() if caduca(v) < ahora]:
        del diccionario[k]


def nueva_sesion() -> str:
    _limpiar(_sesiones, lambda v: v)
    ficha = secrets.token_urlsafe(32)
    _sesiones[ficha] = time.time() + HORAS_DE_SESION * 3600
    return ficha


def sesion_valida(request: Request) -> bool:
    ficha = request.cookies.get(COOKIE_ADMIN, "")
    caduca = _sesiones.get(ficha)
    return bool(ficha) and caduca is not None and caduca > time.time()


def cerrar_sesion(request: Request) -> None:
    _sesiones.pop(request.cookies.get(COOKIE_ADMIN, ""), None)


def nueva_alta() -> tuple[str, str]:
    """Tras acertar la contraseña sin tener aún la verificación en dos pasos: un secreto nuevo
    que no se guarda hasta que se confirme con un código."""
    _limpiar(_altas, lambda v: v[1])
    ficha, secreto = secrets.token_urlsafe(32), nuevo_secreto_totp()
    _altas[ficha] = (secreto, time.time() + MINUTOS_DE_ALTA * 60)
    return ficha, secreto


def alta_pendiente(request: Request) -> str | None:
    dato = _altas.get(request.cookies.get(COOKIE_ALTA, ""))
    return dato[0] if dato and dato[1] > time.time() else None


def terminar_alta(request: Request) -> None:
    _altas.pop(request.cookies.get(COOKIE_ALTA, ""), None)


def poner_cookie(respuesta, request: Request, nombre: str, valor: str, segundos: int) -> None:
    respuesta.set_cookie(nombre, valor, max_age=segundos, path="/admin", httponly=True,
                         secure=es_https(request), samesite="strict")


# --- Intentos fallidos al entrar ---------------------------------------------------------

MAX_FALLOS_POR_IP = 5
MAX_FALLOS_EN_TOTAL = 20          # por si prueban desde muchas IP a la vez
MINUTOS_DE_CASTIGO = 15
_fallos: dict[str, deque] = defaultdict(deque)


def _recientes(cola: deque) -> deque:
    limite = time.time() - MINUTOS_DE_CASTIGO * 60
    while cola and cola[0] < limite:
        cola.popleft()
    return cola


def bloqueado(request: Request) -> bool:
    return (len(_recientes(_fallos[ip(request)])) >= MAX_FALLOS_POR_IP
            or len(_recientes(_fallos["*"])) >= MAX_FALLOS_EN_TOTAL)


def apuntar_fallo(request: Request) -> None:
    _fallos[ip(request)].append(time.time())
    _fallos["*"].append(time.time())


# --- Límite de peticiones ----------------------------------------------------------------

PETICIONES_POR_MINUTO = 120
_peticiones: dict[str, deque] = defaultdict(deque)
_ultima_poda = 0.0


def demasiadas(request: Request) -> bool:
    global _ultima_poda
    ahora = time.time()
    if ahora - _ultima_poda > 300:            # que el diccionario no crezca sin fin
        for k in [k for k, v in _peticiones.items() if not v or v[-1] < ahora - 60]:
            del _peticiones[k]
        _ultima_poda = ahora
    cola = _peticiones[ip(request)]
    while cola and cola[0] < ahora - 60:
        cola.popleft()
    if len(cola) >= PETICIONES_POR_MINUTO:
        return True
    cola.append(ahora)
    return False


# --- Cabeceras y comprobaciones de cada petición -----------------------------------------

def _csp(nonce: str) -> str:
    return "; ".join([
        "default-src 'self'",
        f"script-src 'self' 'nonce-{nonce}'",
        "style-src 'self' 'unsafe-inline'",                  # Leaflet coloca el mapa con style=""
        "img-src 'self' data: https://tile.openstreetmap.org",
        "connect-src 'self' https://nominatim.openstreetmap.org",
        "worker-src 'self'", "manifest-src 'self'",
        "object-src 'none'", "base-uri 'none'", "form-action 'self'", "frame-ancestors 'none'",
    ])


def _misma_web(request: Request) -> bool:
    """Un formulario enviado desde otra web trae su Origin (o Referer). Sin ninguno de los dos
    no es un navegador (curl, un atajo...) y no hay CSRF posible."""
    origen = request.headers.get("origin") or request.headers.get("referer")
    if not origen:
        return True
    return urllib.parse.urlsplit(origen).netloc == request.headers.get("host")


async def middleware(request: Request, call_next):
    estatico = request.url.path.startswith("/static/")
    if not estatico and demasiadas(request):
        return PlainTextResponse("Demasiadas peticiones. Espera un minuto.", status_code=429,
                                 headers={"Retry-After": "60"})
    if request.method not in ("GET", "HEAD", "OPTIONS") and not _misma_web(request):
        return PlainTextResponse("Formulario de otra web.", status_code=403)
    if desde_internet(request) and not es_https(request):
        # Cloudflare deja entrar por http://; aquí se manda siempre a https://.
        return RedirectResponse(str(request.url.replace(scheme="https")), status_code=301)
    request.state.nonce = secrets.token_urlsafe(16)
    if desde_internet(request) and request.url.path.lower().startswith("/admin"):
        # Ni 405 ni redirecciones: desde internet el panel no existe, con ningún método ni ruta.
        respuesta = JSONResponse({"detail": "Not Found"}, status_code=404)
    else:
        respuesta = await call_next(request)
    cabeceras = {
        "Content-Security-Policy": _csp(request.state.nonce),
        "X-Content-Type-Options": "nosniff",
        "X-Frame-Options": "DENY",
        "Referrer-Policy": "strict-origin-when-cross-origin",
        "Permissions-Policy": "geolocation=(self), camera=(), microphone=(), payment=(), usb=()",
        "Cross-Origin-Opener-Policy": "same-origin",
    }
    if es_https(request):
        cabeceras["Strict-Transport-Security"] = "max-age=31536000"
    if request.url.path.startswith("/admin"):
        cabeceras["Cache-Control"] = "no-store"
    for clave, valor in cabeceras.items():
        respuesta.headers.setdefault(clave, valor)
    return respuesta


# --- Terminal ----------------------------------------------------------------------------

def _main(argv: list[str]) -> int:
    import getpass

    from . import db
    if argv[:1] == ["hash"]:
        clave = getpass.getpass("Contraseña del panel: ") if sys.stdin.isatty() else sys.stdin.readline().rstrip("\n")
        if len(clave) < 12:
            print("Mejor de 12 caracteres o más.", file=sys.stderr)
            return 1
        print(hash_clave(clave))
        return 0
    if argv[:1] == ["quitar-2fa"]:
        db.iniciar()
        repo.guardar_secreto("totp", None)
        print("Verificación en dos pasos borrada: se vuelve a dar de alta al entrar en /admin.")
        return 0
    print(__doc__)
    return 1


if __name__ == "__main__":
    sys.exit(_main(sys.argv[1:]))

#!/usr/bin/env python3
"""Crea o actualiza el stack de Pumpcast en Portainer usando su API.

Opcional: solo sirve si usas Portainer. La imagen se construye antes con docker build
y el stack la usa por su etiqueta.

El token NO está aquí: se lee de ~/.config/pumpcast/portainer.env (fuera del
repositorio, chmod 600), con PORTAINER_TOKEN= y PORTAINER_URL=.
Si existe docker-compose.local.yml (ignorado por git), se despliega ese en vez del
docker-compose.yml: ahí van las rutas y redes de cada instalación.

Al crear el stack, si hay un Watchtower que avisa por Telegram, TELEGRAM_TOKEN y
TELEGRAM_CHAT se sacan de él (el mismo bot) y se guardan como variables del stack en
Portainer, nunca en el repositorio. Al actualizarlo se conservan las que ya tenga.

    python3 scripts/portainer.py estado      qué hay ahora
    python3 scripts/portainer.py desplegar   crea el stack o lo actualiza
"""
from __future__ import annotations

import json
import os
import re
import ssl
import subprocess
import sys
import urllib.error
import urllib.request
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
COMPOSE = RAIZ / "docker-compose.local.yml"
if not COMPOSE.is_file():
    COMPOSE = RAIZ / "docker-compose.yml"
ENV_FILE = Path(os.environ.get("PORTAINER_ENV", Path.home() / ".config/pumpcast/portainer.env"))
STACK = os.environ.get("PORTAINER_STACK", "pumpcast")     # el nombre del stack en Portainer
SIN_VERIFICAR = ssl._create_unverified_context()      # Portainer local con certificado propio


def leer_env() -> dict:
    datos = {}
    if ENV_FILE.is_file():
        for linea in ENV_FILE.read_text().splitlines():
            linea = linea.strip()
            if linea and not linea.startswith("#") and "=" in linea:
                clave, valor = linea.split("=", 1)
                datos[clave.strip()] = valor.strip()
    return datos


def api(metodo: str, ruta: str, token: str, base: str, cuerpo=None):
    datos = json.dumps(cuerpo).encode() if cuerpo is not None else None
    peticion = urllib.request.Request(base.rstrip("/") + ruta, data=datos, method=metodo,
                                      headers={"X-API-Key": token, "Content-Type": "application/json"})
    with urllib.request.urlopen(peticion, timeout=60, context=SIN_VERIFICAR) as respuesta:
        texto = respuesta.read().decode()
    return json.loads(texto) if texto.strip() else None


def entorno_local(token: str, base: str) -> int:
    for e in api("GET", "/api/endpoints", token, base):
        if e.get("Type") in (1, 2):                   # Docker local o agente
            return e["Id"]
    raise SystemExit("No encuentro ningún entorno Docker en Portainer.")


def buscar_stack(token: str, base: str):
    for s in api("GET", "/api/stacks", token, base):
        if s.get("Name") == STACK:
            return s
    return None


def telegram_de_watchtower() -> list[dict]:
    """Las variables de Telegram a partir de WATCHTOWER_NOTIFICATION_URL (telegram://token@telegram?channels=id)."""
    try:
        salida = subprocess.run(["docker", "inspect", "watchtower", "--format", "{{json .Config.Env}}"],
                                capture_output=True, text=True, check=True).stdout
    except (OSError, subprocess.CalledProcessError):
        return []
    for variable in json.loads(salida):
        m = re.search(r"telegram://([^@]+)@telegram\?channels=(-?[0-9]+)", variable)
        if m:
            return [{"name": "TELEGRAM_TOKEN", "value": m.group(1)}, {"name": "TELEGRAM_CHAT", "value": m.group(2)}]
    return []


def main() -> int:
    orden = sys.argv[1] if len(sys.argv) > 1 else "estado"
    env = leer_env()
    token, base = env.get("PORTAINER_TOKEN", ""), env.get("PORTAINER_URL", "https://localhost:9443")
    if not token:
        print(f"No hay token en {ENV_FILE}.\n"
              f"Ponlo detrás de PORTAINER_TOKEN= o pega {COMPOSE} a mano en Portainer.")
        return 1

    endpoint = entorno_local(token, base)
    existente = buscar_stack(token, base)
    if orden == "estado":
        print(f"Entorno Portainer: {endpoint}")
        print(f"Stack «{STACK}»: " + (f"existe (id {existente['Id']})" if existente else "no existe todavía"))
        return 0
    if orden != "desplegar":
        print(__doc__)
        return 2

    contenido = COMPOSE.read_text()
    try:
        if existente:
            api("PUT", f"/api/stacks/{existente['Id']}?endpointId={endpoint}", token, base,
                {"stackFileContent": contenido, "env": existente.get("Env", []),
                 "prune": True, "pullImage": False})
            print(f"Stack «{STACK}» actualizado (id {existente['Id']}).")
        else:
            variables = telegram_de_watchtower()
            creado = api("POST", f"/api/stacks/create/standalone/string?endpointId={endpoint}", token, base,
                         {"name": STACK, "stackFileContent": contenido, "env": variables})
            print(f"Stack «{STACK}» creado (id {creado['Id']}). Telegram: "
                  + ("configurado con el bot de Watchtower." if variables else "sin configurar."))
    except urllib.error.HTTPError as e:
        print(f"Portainer ha respondido {e.code}: {e.read().decode()[:400]}")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())

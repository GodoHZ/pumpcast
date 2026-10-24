"""Crea una base de datos de ejemplo (nunca la de verdad) para las capturas.

Toma la lectura real de Madrid centro de los tests como «hoy» y se inventa 150 días atrás que
siguen a un Brent también inventado, para que se vean las gráficas y la previsión.
"""
import json
import math
import os
import random
import sys
from datetime import datetime, time, timedelta

RAIZ = os.environ.get("RAIZ", "/app")
sys.path.insert(0, RAIZ)
os.environ.setdefault("DATA_DIR", "/demo")
from app import db, mercado, minetur, repo  # noqa: E402

db.iniciar()
momento, estaciones = minetur.interpretar(json.load(open(f"{RAIZ}/tests/datos/madrid.json", encoding="utf-8")))
hoy = momento.date()
dia = lambda n: (hoy - timedelta(days=n)).isoformat()  # noqa: E731

brent = {dia(n): 95 + 9 * math.sin(n / 18) + 3 * math.sin(n / 5) for n in range(170, -1, -1)}
mercado.guardar(brent, {d: 1.12 for d in brent})
en_euros = {d: b / 1.12 for d, b in brent.items()}

# Además del Brent, sustos que no tienen que ver con él (como en la vida real), para que la
# previsión de las capturas acierte lo que acertaría de verdad y no un 100 % de mentira.
azar = random.Random(int(os.environ.get("SEMILLA", "7")))
RUIDO = float(os.environ.get("RUIDO", "0.012"))
sustos, acumulado = {}, 0.0
for n in range(150, -1, -1):
    acumulado += azar.gauss(0, RUIDO) + (azar.choice((-0.04, 0.04)) if azar.random() < 0.05 else 0)
    sustos[n] = acumulado

for n in range(150, 0, -1):
    desvio = 0.0075 * (en_euros[dia(n + 9)] - en_euros[dia(9)]) + sustos[n] - sustos[0]
    pasadas = [{**e, "precios": {c: round(p + desvio + 0.004 * math.sin(e["id"] * 7 + n), 3)
                                 for c, p in e["precios"].items()}} for e in estaciones]
    repo.guardar_historico(datetime.combine(hoy - timedelta(days=n), time()), pasadas, "28")
repo.guardar_lectura(momento, estaciones)
repo.guardar_ajustes({"provincias": "28", "lat": "40.4168", "lon": "-3.7038", "radio_km": "5"})
from app import prediccion  # noqa: E402

p = prediccion.prevision(repo.ajustes(), "g95")
print("demo lista:", len(estaciones), "estaciones,", len(brent), "días de Brent; prueba:", p.get("prueba"))

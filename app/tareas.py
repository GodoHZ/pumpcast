"""La tarea de fondo: lee precios cada media hora, rellena el histórico, actualiza el
petróleo y envía los avisos que toquen.

Va dentro de la app (no en un cron suelto), así todo vive en el stack de Portainer.
"""
from __future__ import annotations

import asyncio
import logging
import time
from datetime import datetime, timedelta

from . import avisos, config, mercado, minetur, prediccion, repo

log = logging.getLogger("pumpcast")

DIAS_DE_HISTORICO = 365
DIAS_DE_HISTORICO_POR_CICLO = 10      # unos 30 s por minuto: el histórico se llena en ~40 min
HORAS_ENTRE_MERCADO = 6
_ultimo_mercado = 0.0


def toca_leer(ahora: datetime) -> bool:
    if not repo.provincias(repo.ajustes()):
        return False                    # todavía no se ha elegido provincia
    ultima = repo.ultima_lectura(con_errores=True)
    if not ultima:
        return True
    espera = config.MINUTOS_TRAS_ERROR if ultima["error"] else config.MINUTOS_ENTRE_LECTURAS
    return ahora - datetime.fromisoformat(ultima["momento"]) >= timedelta(minutes=espera)


def leer_ahora() -> bool:
    try:
        for provincia in repo.provincias(repo.ajustes()):
            momento, estaciones = minetur.interpretar(minetur.descargar(provincia))
            repo.guardar_lectura(momento, estaciones)
            log.info("Provincia %s: %d estaciones (datos de %s)", provincia, len(estaciones), momento)
        return True
    except Exception as e:  # noqa: BLE001 - el Ministerio a veces falla; se reintenta luego
        log.warning("No se pudieron leer los precios: %s", e)
        repo.apuntar_error(str(e)[:500])
        return False


def rellenar_historico(ahora: datetime) -> None:
    for provincia in repo.provincias(repo.ajustes()):
        pendientes = repo.dias_sin_historico(provincia, DIAS_DE_HISTORICO, ahora.date())
        for dia in pendientes[:DIAS_DE_HISTORICO_POR_CICLO]:
            try:
                momento, estaciones = minetur.interpretar(minetur.descargar_dia(provincia, dia))
            except Exception as e:  # noqa: BLE001
                log.warning("Histórico %s del %s: %s", provincia, dia, e)
                return
            repo.guardar_historico(momento, estaciones, provincia)
        if pendientes:
            log.info("Histórico %s: quedan %d días", provincia,
                     max(0, len(pendientes) - DIAS_DE_HISTORICO_POR_CICLO))


def actualizar_mercado() -> None:
    global _ultimo_mercado
    if time.monotonic() - _ultimo_mercado < HORAS_ENTRE_MERCADO * 3600 and _ultimo_mercado:
        return
    try:
        mercado.guardar(*mercado.descargar())
        _ultimo_mercado = time.monotonic()
        log.info("Brent y euro/dólar actualizados")
    except Exception as e:  # noqa: BLE001
        log.warning("No se pudo leer el Brent o el euro/dólar: %s", e)


def ciclo() -> None:
    ahora = datetime.now(config.TZ)
    if toca_leer(ahora):
        leer_ahora()
    actualizar_mercado()
    try:
        prediccion.apuntar_de_hoy(repo.ajustes())
    except Exception as e:  # noqa: BLE001
        log.warning("No se pudo calcular la previsión: %s", e)
    try:
        avisos.tarea_avisos(ahora)
    except Exception as e:  # noqa: BLE001
        log.warning("No se pudo enviar el aviso: %s", e)
    rellenar_historico(ahora)


async def bucle() -> None:
    while True:
        await asyncio.to_thread(ciclo)
        await asyncio.sleep(60)

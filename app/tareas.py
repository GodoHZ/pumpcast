"""La tarea de fondo: lee los precios de toda España cada media hora, rellena el histórico,
actualiza el petróleo y envía los avisos que toquen.

Solo esta tarea habla con el Ministerio: las visitas a la web nunca disparan una descarga,
así que da igual cuánta gente la use.

Va dentro de la app (no en un cron suelto), así todo vive en el stack de Portainer.
"""
from __future__ import annotations

import asyncio
import logging
import time
from datetime import date, datetime, timedelta

from . import avisos, config, copias, mercado, minetur, prediccion, repo

log = logging.getLogger("pumpcast")

DIAS_DE_HISTORICO = 365
DIAS_DE_HISTORICO_POR_CICLO = 1       # un día (unos 7 s) por minuto: sin agobiar al Ministerio, ~6 h
HORAS_ENTRE_MERCADO = 6
_ultimo_mercado = 0.0
_ultima_limpieza: date | None = None


def toca_leer(ahora: datetime) -> bool:
    ultima = repo.ultima_lectura(con_errores=True)
    if not ultima:
        return True
    espera = config.MINUTOS_TRAS_ERROR if ultima["error"] else config.MINUTOS_ENTRE_LECTURAS
    return ahora - datetime.fromisoformat(ultima["momento"]) >= timedelta(minutes=espera)


def leer_ahora() -> bool:
    try:
        momento, estaciones = minetur.interpretar(minetur.descargar())
        repo.guardar_lectura(momento, estaciones)
        log.info("España: %d estaciones (datos de %s)", len(estaciones), momento)
        return True
    except Exception as e:  # noqa: BLE001 - el Ministerio a veces falla; se reintenta luego
        log.warning("No se pudieron leer los precios: %s", e)
        repo.apuntar_error(str(e)[:500])
        return False


def rellenar_historico(ahora: datetime) -> None:
    hoy = ahora.date()
    pendientes = repo.dias_sin_historico(DIAS_DE_HISTORICO, hoy)
    for dia in pendientes[:DIAS_DE_HISTORICO_POR_CICLO]:
        try:
            momento, estaciones = minetur.interpretar(minetur.descargar_dia(dia))
        except Exception as e:  # noqa: BLE001
            log.warning("Histórico del %s: %s", dia, e)
            return
        repo.guardar_historico(momento, estaciones,
                               con_precios=dia > hoy - timedelta(days=config.DIAS_CON_PRECIOS))
    if pendientes:
        log.info("Histórico: quedan %d días", max(0, len(pendientes) - DIAS_DE_HISTORICO_POR_CICLO))


def limpiar(hoy: date) -> None:
    """Una vez al día, los precios de cada gasolinera que ya no hacen falta."""
    global _ultima_limpieza
    if _ultima_limpieza == hoy:
        return
    borrados = repo.borrar_precios_viejos(hoy)
    _ultima_limpieza = hoy
    if borrados:
        log.info("Borrados %d precios de hace más de %d días", borrados, config.DIAS_CON_PRECIOS)


def actualizar_mercado() -> None:
    global _ultimo_mercado
    if time.monotonic() - _ultimo_mercado < HORAS_ENTRE_MERCADO * 3600 and _ultimo_mercado:
        return
    try:
        mercado.guardar(*mercado.descargar())
        _ultimo_mercado = time.monotonic()
        log.info("Brent, gasóleo, gasolina y euro/dólar actualizados")
    except Exception as e:  # noqa: BLE001
        log.warning("No se pudo leer el Brent o el euro/dólar: %s", e)


def ciclo() -> None:
    ahora = datetime.now(config.TZ)
    if toca_leer(ahora):
        leer_ahora()
    actualizar_mercado()
    try:
        prediccion.apuntar_de_hoy()
    except Exception as e:  # noqa: BLE001
        log.warning("No se pudo calcular la previsión: %s", e)
    try:
        avisos.tarea_avisos(ahora)
    except Exception as e:  # noqa: BLE001
        log.warning("No se pudo enviar el aviso: %s", e)
    rellenar_historico(ahora)
    limpiar(ahora.date())
    try:
        copias.hacer(ahora.date())
    except Exception as e:  # noqa: BLE001
        log.warning("No se pudo hacer la copia: %s", e)


async def bucle() -> None:
    while True:
        await asyncio.to_thread(ciclo)
        await asyncio.sleep(60)

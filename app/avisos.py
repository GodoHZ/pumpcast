"""Avisos por Telegram: el resumen de cada mañana y los chollos.

Son del dueño de la instalación: su ubicación y sus preferencias están en el panel de
administración, no en las de los visitantes."""
from __future__ import annotations

import html
import urllib.parse
import urllib.request
from datetime import datetime
from statistics import mean

from . import config, i18n, prediccion, repo
from .formato import km, moneda, numero

DIAS_MINIMOS_PARA_CHOLLOS = 7     # sin histórico no se sabe qué es barato


def configurado() -> bool:
    return bool(config.TELEGRAM_TOKEN and config.TELEGRAM_CHAT)


def idioma(aj: dict) -> str:
    return aj["idioma"] if aj["idioma"] in i18n.IDIOMAS else "es"


def enviar(texto: str) -> None:
    if not configurado():
        raise RuntimeError("Faltan TELEGRAM_TOKEN y TELEGRAM_CHAT.")
    campos = {"chat_id": config.TELEGRAM_CHAT, "text": texto, "parse_mode": "HTML",
              "disable_web_page_preview": "true"}
    if config.TELEGRAM_THREAD:
        campos["message_thread_id"] = config.TELEGRAM_THREAD     # un tema concreto de un grupo
    datos = urllib.parse.urlencode(campos).encode()
    urllib.request.urlopen(f"https://api.telegram.org/bot{config.TELEGRAM_TOKEN}/sendMessage",
                           datos, timeout=30).close()


def _sitio(e: dict, lang: str) -> str:
    return f"{html.escape(e['rotulo'].title())}, {html.escape(e['municipio'])} ({km(e['distancia'], lang)})"


def _enlace() -> str:
    return f"\n{config.APP_URL}" if config.APP_URL else ""


def resumen_diario(aj: dict, comb: str, lang: str = "es") -> str | None:
    lista = repo.cercanas(aj, comb)
    if not lista:
        return None
    t = lambda clave, **h: i18n.t(lang, clave, **h)  # noqa: E731
    media = mean(e["precio"] for e in lista)
    litros = float(aj["litros"])
    lineas = [t("tg.hoy", comb=t("comb." + comb), radio=aj["radio_km"]) + "\n"]
    for i, e in enumerate(lista[:3], 1):
        lineas.append(f"{i}. <b>{moneda(e['precio'], 3, lang)}</b> · {_sitio(e, lang)}")
    ahorro = (media - lista[0]["precio"]) * litros
    lineas.append("\n" + t("tg.media", media=moneda(media, 3, lang), litros=f"{litros:g}",
                           coste=moneda(lista[0]["precio"] * litros, 2, lang), ahorro=moneda(ahorro, 2, lang)))
    serie = repo.serie_zona(aj, comb, dias=8)
    if len(serie) >= 2:
        cambio = (serie[-1]["media"] - serie[0]["media"]) * 100
        if abs(cambio) >= 0.5:
            lineas.append(t("tg.sube" if cambio > 0 else "tg.baja", cts=numero(abs(cambio), 1, lang)))
        else:
            lineas.append(t("tg.igual"))
    p = prediccion.prevision(repo.provincia_de(float(aj["lat"]), float(aj["lon"])), comb, litros)
    if p["lista"]:
        lineas.append(f"\n{p['icono']} <b>{prediccion.titulo(p, lang)}</b>. {prediccion.frase(p, lang)}")
    return "\n".join(lineas) + _enlace()


def chollo(aj: dict, comb: str, lang: str = "es") -> tuple[str, str] | None:
    """Si la más barata de hoy está bastante por debajo de la media de 30 días: (clave, texto)."""
    lista = repo.cercanas(aj, comb)
    serie = repo.serie_zona(aj, comb, dias=30)
    if not lista or len(serie) < DIAS_MINIMOS_PARA_CHOLLOS:
        return None
    media_30 = mean(f["media"] for f in serie)
    mejor = lista[0]
    if mejor["precio"] > media_30 - float(aj["umbral_chollo"]):
        return None
    texto = i18n.t(lang, "tg.chollo", comb=i18n.t(lang, "comb." + comb), precio=moneda(mejor["precio"], 3, lang),
                   sitio=_sitio(mejor, lang), cts=numero((media_30 - mejor["precio"]) * 100, 1, lang),
                   media=moneda(media_30, 3, lang))
    return f"chollo:{serie[-1]['fecha']}:{mejor['id']}", texto + _enlace()


def tarea_avisos(ahora: datetime) -> None:
    if not configurado():
        return
    aj = repo.ajustes()
    comb, lang = aj["combustible"], idioma(aj)
    clave_diaria = f"diario:{ahora.date().isoformat()}"
    if (aj["aviso_diario"] == "1" and ahora.strftime("%H:%M") >= aj["hora_aviso"]
            and not repo.aviso_enviado(clave_diaria)):
        texto = resumen_diario(aj, comb, lang)
        if texto:
            enviar(texto)
            repo.marcar_aviso(clave_diaria)
    if aj["avisos_chollo"] == "1" and 8 <= ahora.hour < 22:      # de noche no molesta
        encontrado = chollo(aj, comb, lang)
        if encontrado and not repo.aviso_enviado(encontrado[0]):
            enviar(encontrado[1])
            repo.marcar_aviso(encontrado[0])

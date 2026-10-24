from datetime import datetime

import pytest

from app import avisos, config, repo


@pytest.fixture
def telegram(monkeypatch):
    """Telegram configurado, pero los mensajes se quedan en una lista."""
    enviados = []
    monkeypatch.setattr(config, "TELEGRAM_TOKEN", "token-de-prueba")
    monkeypatch.setattr(config, "TELEGRAM_CHAT", "123")
    monkeypatch.setattr(avisos, "enviar", enviados.append)
    return enviados


def _hora(h, m=0):
    return datetime(2026, 10, 24, h, m, tzinfo=config.TZ)


def test_resumen_diario(cargada):
    texto = avisos.resumen_diario(repo.ajustes(), "g95")
    assert "Gasolina 95 hoy" in texto
    assert "1." in texto and "3." in texto
    assert "ahorras" in texto


def test_sin_telegram_no_hace_nada(cargada):
    avisos.tarea_avisos(_hora(9))        # no debe intentar enviar ni fallar


def test_el_resumen_sale_una_vez_y_a_su_hora(cargada, telegram):
    avisos.tarea_avisos(_hora(8, 0))
    assert telegram == []                 # todavía no son las 08:30
    avisos.tarea_avisos(_hora(8, 30))
    avisos.tarea_avisos(_hora(12, 0))
    assert len(telegram) == 1


def test_resumen_desactivado(cargada, telegram):
    repo.guardar_ajustes({"aviso_diario": "0"})
    avisos.tarea_avisos(_hora(9))
    assert telegram == []


def test_sin_historico_no_hay_chollos(cargada, telegram):
    assert avisos.chollo(repo.ajustes(), "g95") is None


def test_chollo_cuando_baja_mucho(con_historial, telegram):
    repo.guardar_ajustes({"aviso_diario": "0"})
    avisos.tarea_avisos(_hora(10))
    avisos.tarea_avisos(_hora(11))
    assert len(telegram) == 1
    assert "Chollo" in telegram[0]


def test_de_noche_no_avisa_de_chollos(con_historial, telegram):
    repo.guardar_ajustes({"aviso_diario": "0"})
    avisos.tarea_avisos(_hora(23))
    assert telegram == []


def test_sin_bajada_no_hay_chollo(con_historial):
    repo.guardar_ajustes({"umbral_chollo": "0.5"})
    assert avisos.chollo(repo.ajustes(), "g95") is None

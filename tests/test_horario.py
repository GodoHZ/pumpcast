from datetime import datetime, timedelta

from app import config, horario


def _a_las(dia: int, hora: int, minuto: int = 0) -> datetime:
    """Una hora de la semana del 26/10/2026 (lunes = 0), en hora de Madrid."""
    return datetime(2026, 10, 26, hora, minuto, tzinfo=config.TZ) + timedelta(days=dia)


def test_24_horas():
    assert horario.estado("L-D: 24H", _a_las(2, 3))["clave"] == "24h"
    assert horario.estado("L-D: 00:00-23:59", _a_las(6, 23, 30))["clave"] == "24h"


def test_abierta_y_cerrada():
    h = "L-V: 06:00-22:00; S: 08:00-14:00 y 17:00-21:00"
    assert horario.estado(h, _a_las(0, 21)) == {"abierta": True, "clave": "cierra", "hora": "22:00"}
    assert horario.estado(h, _a_las(0, 5)) == {"abierta": False, "clave": "abre", "hora": "06:00"}
    assert horario.estado(h, _a_las(5, 15)) == {"abierta": False, "clave": "abre", "hora": "17:00"}
    assert horario.estado(h, _a_las(6, 12)) == {"abierta": False, "clave": "cerrada", "hora": None}


def test_pasada_la_medianoche():
    assert horario.estado("L-D: 06:00-02:00", _a_las(1, 1))["abierta"] is True
    assert horario.estado("L-D: 06:00-02:00", _a_las(1, 23))["hora"] == "02:00"
    assert horario.estado("L-D: 06:00-02:00", _a_las(1, 3))["abierta"] is False


def test_lo_que_no_se_entiende_es_desconocido():
    for texto in (None, "", "L: 06:00-22:00", "Lunes a viernes de 6 a 22", "L-D: 6-22"):
        assert horario.estado(texto, _a_las(0, 12)) is None
    assert horario.abierta({"horario": "raro"}, _a_las(0, 12)) is True


def test_canarias_va_una_hora_menos():
    h = "L-D: 07:00-22:00"
    assert horario.estado(h, _a_las(0, 22, 30))["abierta"] is False
    assert horario.estado(h, _a_las(0, 22, 30), provincia_id="35")["abierta"] is True

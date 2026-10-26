from datetime import date, datetime, timedelta
from math import sin

from app import db, mercado, prediccion, repo

HOY = date(2026, 10, 24)


def _dia(n: int) -> str:
    return (HOY - timedelta(days=n)).isoformat()


def _sintetico(dias=200, retraso=10, pendiente=0.008):
    """Un Brent que sube y baja, y una gasolina que lo sigue `retraso` días después."""
    brent = {_dia(n): 80 + 12 * sin(n / 15) for n in range(dias + 40, -1, -1)}
    precios = {_dia(n): 0.9 + pendiente * brent[_dia(n + retraso)] + 0.001 * sin(n * 1.7)
               for n in range(dias, -1, -1)}
    return precios, brent


def test_si_el_brent_sube_la_gasolina_va_detras():
    precios, brent = _sintetico(retraso=10)
    coef = prediccion.ajustar(precios, brent)
    assert coef[1] > 0                                   # más Brent la semana pasada, más subida
    subida = {**brent, **{_dia(n): brent[_dia(n)] + 2 * (8 - n) for n in range(1, 8)}}
    bajada = {**brent, **{_dia(n): brent[_dia(n)] - 2 * (8 - n) for n in range(1, 8)}}
    assert prediccion._prever(_dia(0), precios, subida, coef) > prediccion._prever(_dia(0), precios, bajada, coef)


def test_la_prueba_acierta_con_datos_limpios():
    precios, brent = _sintetico()
    prueba = prediccion._prueba(precios, brent)
    assert prueba["total"] > 40
    assert prueba["aciertos"] / prueba["total"] > 0.8


def test_no_mira_al_futuro():
    """El Brent de mañana no puede influir en la previsión de hoy."""
    precios, brent = _sintetico(retraso=3)
    coef = prediccion.ajustar(precios, brent)
    antes = prediccion._prever(_dia(0), precios, brent, coef)
    trucado = {**brent, _dia(0): 500.0, (HOY + timedelta(days=1)).isoformat(): 500.0}
    assert prediccion._prever(_dia(0), precios, trucado, coef) == antes
    # y al aprender para la prueba, los días después del corte no cuentan
    corte = _dia(60)
    trucados = {f: (p + 1 if f > corte else p) for f, p in precios.items()}
    assert prediccion.ajustar(precios, brent, hasta=corte) == prediccion.ajustar(trucados, brent, hasta=corte)


def test_sin_datos_suficientes(monkeypatch):
    precios, brent = _sintetico(dias=30)
    monkeypatch.setattr(prediccion, "_datos", lambda provincia, comb: precios)
    p = prediccion.prevision("28", "g95", brent=brent)
    assert not p["lista"] and p["faltan"] > 0
    assert not prediccion.prevision(None, "g95", brent=brent)["lista"]     # sitio sin gasolineras cerca


def test_prevision_completa_y_se_apunta(monkeypatch, cargada):
    precios, brent = _sintetico()
    monkeypatch.setattr(prediccion, "_datos", lambda provincia, comb: precios)
    monkeypatch.setattr(prediccion.mercado, "brent_euros", lambda: brent)
    p = prediccion.prevision("28", "g95", litros=50)
    assert p["lista"] and p["semaforo"] in prediccion.SEMAFOROS
    assert p["nombre_provincia"] == "Madrid"
    assert p["prueba"]["total"] > 0
    assert round(p["euros_deposito"], 6) == round(abs(p["cambio"]) * 50, 6)
    assert prediccion.frase(p, "es") and prediccion.frase(p, "en") != prediccion.frase(p, "es")
    apuntadas = prediccion.apuntar_de_hoy()         # una por combustible de Madrid, el día de los datos
    assert apuntadas == len({c for e in cargada[1] for c in e["precios"]})
    assert prediccion.apuntar_de_hoy() == 0         # y solo una vez
    with db.sesion() as con:
        assert con.execute("SELECT COUNT(DISTINCT provincia) FROM previsiones").fetchone()[0] == 1


def test_semaforo_y_aciertos():
    assert prediccion.semaforo(0.03) == "llena"
    assert prediccion.semaforo(-0.03) == "espera"
    assert prediccion.semaforo(0.005) == "igual"
    assert prediccion.acierta("llena", 0.01)
    assert not prediccion.acierta("espera", 0.01)
    assert prediccion.acierta("igual", -0.01)


def test_lectores_del_mercado():
    assert mercado.brent_fred("observation_date,DCOILBRENTEU\n2026-10-20,115.22\n2026-10-21,.\n") == {
        "2026-10-20": 115.22}
    bce = "KEY,FREQ,TIME_PERIOD,OBS_VALUE\nx,D,2026-10-23,1.1193\n"
    assert mercado.eurusd_bce(bce) == {"2026-10-23": 1.1193}


def test_brent_en_euros_rellena_fines_de_semana():
    mercado.guardar({"2026-10-23": 112.0}, {"2026-10-23": 1.12})
    mercado.guardar({"2026-10-26": 100.8}, {"2026-10-26": 1.12})
    serie = mercado.brent_euros()
    assert serie["2026-10-23"] == serie["2026-10-24"] == serie["2026-10-25"]    # viernes a domingo
    assert round(serie["2026-10-25"], 6) == 100.0
    assert round(serie["2026-10-26"], 6) == 90.0


def test_el_brent_acaba_en_el_ultimo_publicado():
    """FRED va una semana por detrás del euro/dólar: no se inventan días con el Brent viejo, y lo
    que quedara de otra fuente más allá de su último dato se borra."""
    mercado.guardar({"2026-10-20": 112.0, "2026-10-26": 999.0}, {"2026-10-20": 1.12})
    mercado.guardar({"2026-10-20": 112.0}, {"2026-10-26": 1.12})
    serie = mercado.brent_euros()
    assert max(serie) == "2026-10-20" and 999.0 / 1.12 not in serie.values()


def test_historico_no_cuenta_como_lectura(lectura):
    momento, estaciones = lectura
    repo.guardar_historico(datetime(2026, 10, 20), estaciones)
    assert repo.ultima_lectura(con_errores=True) is None
    faltan = repo.dias_sin_historico(5, HOY)
    assert date(2026, 10, 20) not in faltan and len(faltan) == 4
    with db.sesion() as con:
        assert con.execute("SELECT COUNT(*) FROM precios WHERE fecha = '2026-10-20'").fetchone()[0] > 0
        assert con.execute("SELECT COUNT(*) FROM medias_provincia WHERE fecha = '2026-10-20'").fetchone()[0] > 0


def test_historico_antiguo_solo_guarda_medias(lectura):
    """Los días viejos del histórico de toda España no llenan la base de datos de precios sueltos."""
    momento, estaciones = lectura
    repo.guardar_historico(datetime(2026, 1, 10), estaciones, con_precios=False)
    serie = repo.serie_provincia("28", "g95")
    assert [f["fecha"] for f in serie] == ["2026-01-10"]
    g95 = [e["precios"]["g95"] for e in estaciones if "g95" in e["precios"]]
    assert abs(serie[0]["media"] - sum(g95) / len(g95)) < 1e-9 and serie[0]["minimo"] == min(g95)
    with db.sesion() as con:
        assert con.execute("SELECT COUNT(*) FROM precios").fetchone()[0] == 0

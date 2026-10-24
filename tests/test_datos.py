from datetime import datetime

from app import config, db, minetur, repo
from app.formato import centimos, euros, km

from conftest import DATOS


def test_interpreta_la_lectura_real(lectura):
    momento, estaciones = lectura
    assert momento == datetime.strptime(DATOS["Fecha"], "%d/%m/%Y %H:%M:%S")
    assert len(estaciones) > 100
    cruda = DATOS["ListaEESSPrecio"][0]
    e = next(x for x in estaciones if x["id"] == int(cruda["IDEESS"]))
    assert e["rotulo"] == cruda["Rótulo"].strip()
    for clave, campo in config.COMBUSTIBLES.items():
        if cruda[campo]:
            assert e["precios"][clave] == float(cruda[campo].replace(",", "."))
    assert abs(e["lat"] - float(cruda["Latitud"].replace(",", "."))) < 1e-9


def test_descarta_las_de_venta_restringida():
    cooperativa = {**DATOS["ListaEESSPrecio"][0], "IDEESS": "999999", "Tipo Venta": "R"}
    _, estaciones = minetur.interpretar({**DATOS, "ListaEESSPrecio": [cooperativa]})
    assert estaciones == []


def test_guardar_dos_veces_el_mismo_dia_no_duplica(lectura):
    repo.guardar_lectura(*lectura)
    repo.guardar_lectura(*lectura)
    with db.sesion() as con:
        filas = con.execute("SELECT COUNT(*) FROM precios WHERE fecha = ?",
                            (lectura[0].date().isoformat(),)).fetchone()[0]
    assert filas == sum(len(e["precios"]) for e in lectura[1])


def test_cercanas_ordenadas_y_dentro_del_radio(cargada):
    aj = repo.ajustes()
    lista = repo.cercanas(aj, "g95")
    assert lista
    assert all(e["distancia"] <= float(aj["radio_km"]) for e in lista)
    assert [e["precio"] for e in lista] == sorted(e["precio"] for e in lista)


def test_cambiar_el_radio_cambia_la_lista(cargada):
    aj = repo.ajustes()
    cerca = repo.cercanas({**aj, "radio_km": "2"}, "g95")
    lejos = repo.cercanas({**aj, "radio_km": "8"}, "g95")
    assert len(cerca) < len(lejos)


def test_serie_y_dia_de_la_semana(con_historial):
    aj = repo.ajustes()
    serie = repo.serie_zona(aj, "g95", dias=30)
    assert len(serie) == 11
    assert serie[-1]["media"] < serie[0]["media"]          # hoy es 10 céntimos más barato
    semana = repo.por_dia_semana(serie)
    assert sum(d["dias"] for d in semana) == 11


def test_precios_actuales_de_una_estacion(cargada, una):
    assert repo.precios_actuales(una["id"])["g95"] == una["precios"]["g95"]


def test_ajustes_se_guardan_y_se_ignoran_las_claves_raras():
    repo.guardar_ajustes({"radio_km": "25", "inventada": "x"})
    aj = repo.ajustes()
    assert aj["radio_km"] == "25"
    assert "inventada" not in aj
    assert aj["combustible"] == config.AJUSTES_POR_DEFECTO["combustible"]


def test_distancia():
    assert repo.distancia_km(40.4168, -3.7038, 40.4168, -3.7038) == 0
    assert 500 < repo.distancia_km(40.4168, -3.7038, 41.3874, 2.1686) < 510   # Madrid-Barcelona


def test_formato():
    assert euros(1.4589) == "1,459"
    assert euros(1234.5, 2) == "1.234,50"
    assert centimos(0.032) == "+3,2"
    assert centimos(-0.01) == "−1,0"
    assert centimos(0.0001) == "0,0"
    assert km(0.35) == "350 m"
    assert km(3.24) == "3,2 km"


def test_numeros_del_ministerio():
    assert minetur._numero("1,799") == 1.799
    assert minetur._numero("") is None
    assert minetur._numero(None) is None

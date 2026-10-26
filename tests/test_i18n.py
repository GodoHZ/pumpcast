import string

from app import config, i18n
from app.formato import centimos, km, moneda


def _huecos(texto: str) -> set[str]:
    return {nombre for _, nombre, _, _ in string.Formatter().parse(texto) if nombre}


def test_los_dos_idiomas_tienen_los_mismos_textos():
    assert set(i18n.TEXTOS["es"]) == set(i18n.TEXTOS["en"])


def test_y_los_mismos_huecos():
    for clave, texto in i18n.TEXTOS["es"].items():
        assert _huecos(texto) == _huecos(i18n.TEXTOS["en"][clave]), clave


def test_hay_nombre_para_cada_combustible():
    for lang in i18n.IDIOMAS:
        for clave in config.COMBUSTIBLES:
            assert i18n.t(lang, "comb." + clave)


def test_idioma_del_navegador():
    assert i18n.del_navegador("es-ES,es;q=0.9,en;q=0.8") == "es"
    assert i18n.del_navegador("en-GB,en;q=0.9") == "en"
    assert i18n.del_navegador("fr-FR,de;q=0.8") == "en"
    assert i18n.del_navegador(None) == "en"
    assert i18n.elegir("es", "en-GB") == "es"
    assert i18n.elegir("auto", "es") == "es"


def test_numeros_en_cada_idioma():
    assert moneda(4.594, 2, "es") == "4,59 €"
    assert moneda(4.594, 2, "en") == "€4.59"
    assert moneda(-1, 2, "en") == "−€1.00"
    assert centimos(0.032, "en") == "+3.2"
    assert km(3.24, "en") == "3.2 km"


def test_provincias():
    assert len(config.PROVINCIAS) == 52
    assert config.NOMBRE_PROVINCIA["04"] == "Almería"
    assert config.NOMBRE_PROVINCIA["28"] == "Madrid"

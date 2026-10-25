# Pumpcast

**Gasolineras baratas cerca de casa y si sale a cuenta llenar hoy.** ⛽ 🇪🇸

[![tests](https://github.com/GodoHZ/pumpcast/actions/workflows/tests.yml/badge.svg)](https://github.com/GodoHZ/pumpcast/actions/workflows/tests.yml)
[![licencia: MIT](https://img.shields.io/badge/licencia-MIT-blue.svg)](LICENSE)

[English](README.md) · **Español**

App web para autoalojar que encuentra las **gasolineras más baratas cerca de tu casa**, guarda
su histórico de precios y te dice si **sale a cuenta llenar hoy o esperar** unos días. Un
contenedor, un fichero SQLite, sin cuentas, sin claves de API y sin rastreo.

Usa los precios oficiales que toda gasolinera de España tiene que comunicar al Ministerio,
actualizados cada 30 minutos.

| Cerca | ¿Lleno o espero? | Mapa | Ajustes |
|---|---|---|---|
| <img src="docs/inicio-es.png" width="200"> | <img src="docs/tendencia-es.png" width="200"> | <img src="docs/mapa-es.png" width="200"> | <img src="docs/ajustes-es.png" width="200"> |

## Qué hace

- **Cerca**: la más barata dentro de tu radio, lo que te cuesta tu repostaje habitual,
  cuánto ahorras frente a la media de la zona y el resto ordenadas por precio, con botón de *Cómo llegar*.
- **¿Lleno hoy o espero?** Un semáforo a 7 días (🟢 llena ya · 🟡 da igual · 🔴 espera si
  puedes), aprendido con un año de precios de *tu* zona: el surtidor va detrás del Brent y
  los precios tienen inercia. Se **prueba con los últimos 60 días sin usarlos para aprender**
  y apunta cada previsión, así que en pantalla ves cuánto acierta de verdad.
- **Tendencia**: media y precio más barato de cada día con el Brent encima, cambio a 7 y 30
  días, y qué día de la semana suele salir más barato.
- **Mapa** de todas las gasolineras de tus provincias, de verde (barata) a rojo (cara).
- **Historial de cada gasolinera**: 90 días de precios frente a la media de la zona.
- **Avisos por Telegram** (opcionales): un resumen cada mañana y un aviso cuando una cercana
  baja bastante de su media de 30 días.
- **Fácil de poner en marcha**: busca tu dirección, toca el mapa o usa el GPS; la provincia
  se elige sola.
- **Instalable como app (PWA)**: añádela a la pantalla de inicio; se abre a pantalla completa
  y, sin conexión, enseña lo último que vio.
- **En castellano e inglés**, según el navegador o lo que elijas en Ajustes.

### ¿Cuánto acierta la previsión?

Sinceramente: es una pista, no una bola de cristal. Con un año de precios reales de una
provincia, en 60 días que no había visto, acertó **unas 6 de cada 10 veces** tanto en
gasolina como en diésel, frente a 4 o 5 de cada 10 si simplemente supones que el precio no
cambia. 2026 ha sido un año loco para los carburantes, con saltos que no tenían nada que ver
con el petróleo, y ningún modelo ve venir guerras, cambios de impuestos ni puentes. Por eso
la app enseña su propio marcador en vez de pedirte que te fíes.

El modelo es sencillo a propósito y vive en `app/prediccion.py`:

```
cambio en 7 días = a + b · (Brent en € la última semana) + c · (precio de la zona la última semana)
```

Una versión más elaborada, que buscaba el retraso exacto respecto al Brent, no acertaba más
que decir «no cambia», así que se descartó.

## Puesta en marcha

```bash
git clone https://github.com/GodoHZ/pumpcast.git && cd pumpcast
docker compose up -d --build
```

Abre `http://127.0.0.1:8098`, entra en **Ajustes**, busca tu dirección y guarda. Los primeros
precios llegan en un minuto. Por detrás, la app descarga un año de histórico de tu provincia
(unos 40 minutos) y la previsión aparece cuando hay datos suficientes.

El contenedor corre como el usuario `1000:1000` y escribe en `./data`. Si el tuyo es otro,
cambia la línea `user:` del `docker-compose.yml` por lo que diga `id -u`.

Para actualizar: `git pull && docker compose up -d --build`.

### Configuración

Todo lo demás se cambia desde **Ajustes**. El contenedor admite unas pocas variables:

| Variable | Para qué | Por defecto |
|---|---|---|
| `TZ` | zona horaria (la usa el resumen de la mañana) | `Europe/Madrid` |
| `PROVINCIAS` | provincia(s) de inicio, [códigos del INE](https://www.ine.es/daco/daco42/codmun/cod_provincia.htm) como `28` o `28,45` | ninguna: se elige en Ajustes |
| `TELEGRAM_TOKEN`, `TELEGRAM_CHAT` | avisos por Telegram | apagados |
| `TELEGRAM_THREAD` | id del tema, si `TELEGRAM_CHAT` es un grupo con temas | — |
| `APP_URL` | enlace que se añade al final de cada aviso | ninguno |
| `DATA_DIR` | dónde vive `pumpcast.db` | `/app/data` |

**Telegram**: crea un bot con [@BotFather](https://t.me/BotFather), escríbele cualquier cosa y
abre `https://api.telegram.org/bot<TOKEN>/getUpdates` para ver tu chat id.

### Seguridad

- **No la expongas a internet.** Escucha en `127.0.0.1` a propósito. Llega a ella por una VPN
  (Tailscale, WireGuard) o por un proxy inverso con HTTPS dentro de tu red.
- **No tiene cuentas de usuario**: es para una casa. Quien llegue a ella puede cambiar los ajustes.
- No guarda ningún dato personal salvo la ubicación de tu casa, en el fichero SQLite.

## De dónde salen los datos

| Dato | Fuente |
|---|---|
| Precios, de hoy y de días pasados | [Geoportal de carburantes](https://geoportalgasolineras.es), Ministerio para la Transición Ecológica (API REST pública) |
| Brent | Yahoo Finance (`BZ=F`) y, si falla, [FRED](https://fred.stlouisfed.org/series/DCOILBRENTEU) |
| Euro/dólar | [Banco Central Europeo](https://data.ecb.europa.eu) |
| Buscador de direcciones y mapa | [OpenStreetMap](https://www.openstreetmap.org/copyright) (Nominatim) |

Yahoo Finance no es una API oficial y puede cambiar; entonces la app tira de FRED, que va
unos días por detrás. El servidor del Ministerio solo habla un cifrado TLS antiguo
(AES256-GCM-SHA384), que la app activa solo para ese servidor.

## Cómo está hecha

Python 3.12, FastAPI y SQLite, plantillas Jinja2, Chart.js y Leaflet (incluidos, para que
funcione sin conexión). Sin compilar nada: no hay npm ni bundler.

```
app/
  main.py        rutas web y arranque          i18n.py      textos en castellano e inglés
  minetur.py     precios del Ministerio        mercado.py   Brent y euro/dólar
  prediccion.py  la previsión a 7 días         avisos.py    avisos por Telegram
  repo.py        consultas SQL                 db.py        esquema
  tareas.py      tarea de fondo: lecturas, histórico y avisos
  templates/     pantallas y service worker    static/      CSS, JS, iconos y librerías
tests/           pytest, se ejecutan dentro del docker build
scripts/         iconos, capturas con WebKit, despliegue en Portainer, hook de git
```

Los **tests se ejecutan durante `docker build`**: si falla uno, no se genera la imagen.

```bash
docker build --target test -t pumpcast-test .                  # solo los tests
docker build -f scripts/capturas/Dockerfile --target export \
  --output type=local,dest=/tmp/capturas .                        # capturas a tamaño iPhone
```

Si vas a tocar el código en tu copia, hay un hook que impide commitear datos privados
(rutas, dominios, `.db`, configuración local): `git config core.hooksPath scripts/git-hooks`.
La lista de patrones se lee de `~/.config/pumpcast/patrones-privados.txt`.

Se aceptan issues y pull requests, sobre todo idiomas nuevos: añade un bloque a
`app/i18n.py` y los tests comprueban que no falte ningún texto.

## Licencia

[MIT](LICENSE). Sin relación con el Ministerio ni con ninguna marca de carburantes.

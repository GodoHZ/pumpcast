# Pumpcast

**Cheap fuel near you, and whether to fill up today.** ⛽ 🇪🇸

[![tests](https://github.com/GodoHZ/pumpcast/actions/workflows/tests.yml/badge.svg)](https://github.com/GodoHZ/pumpcast/actions/workflows/tests.yml)
[![license: MIT](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

**English** · [Español](README.es.md)

A self-hosted web app that finds the **cheapest petrol stations near your home in Spain**,
keeps their price history and tells you whether it's worth **filling up today or waiting**
a few days. One container, one SQLite file, no accounts, no API keys, no tracking.

It uses the official prices that every station in Spain must report to the Ministry, refreshed
every 30 minutes.

| Nearby | Fill up or wait? | Map | Settings |
|---|---|---|---|
| <img src="docs/inicio-en.png" width="200"> | <img src="docs/tendencia-en.png" width="200"> | <img src="docs/mapa-en.png" width="200"> | <img src="docs/ajustes-en.png" width="200"> |

## What it does

- **Nearby**: the cheapest station within your radius, how much you save on a full tank
  compared with the local average, and the rest sorted by price, with a *Directions* button.
- **Fill up today or wait?** A 7-day traffic light (🟢 fill up now · 🟡 no rush · 🔴 wait if
  you can), learnt from a year of prices in *your* area: pumps trail Brent crude, and prices
  have momentum. It is **tested on the last 60 days without learning from them** and logs
  every forecast, so the screen shows how often it actually gets it right.
- **Trends**: local average and cheapest price per day with Brent on top, change over
  7 and 30 days, and which day of the week tends to be cheapest.
- **Map** of every station in your provinces, from green (cheap) to red (expensive).
- **Station history**: 90 days of prices against the local average.
- **Telegram alerts** (optional): a morning summary and a heads-up when a station near you
  drops well below its 30-day average.
- **Easy setup**: search your address, tap the map or use GPS; the province is picked for you.
- **Installable app (PWA)**: add it to your home screen; it opens full screen and shows the
  last data it saw when you're offline.
- **English and Spanish**, following your browser or chosen in Settings.

### How good is the forecast?

Honestly: a hint, not a crystal ball. With a year of real prices from one province, over 60
days it had never seen, it was right about **6 times out of 10** for both petrol and diesel,
against 4–5 out of 10 for simply assuming prices won't change. 2026 was a wild year for fuel,
with jumps that had nothing to do with oil, and no model sees wars, tax changes or bank
holidays coming. That's why the app shows its own track record instead of asking you to
trust it.

The model is deliberately simple and lives in `app/prediccion.py`:

```
change in 7 days = a + b · (Brent in € over the last week) + c · (local price over the last week)
```

A fancier version that looked for the exact lag behind Brent did no better than "no change",
so it was dropped.

## Quick start

```bash
git clone https://github.com/GodoHZ/pumpcast.git && cd pumpcast
docker compose up -d --build
```

Open `http://127.0.0.1:8098`, go to **Settings**, search your address and save. The first
prices arrive within a minute. In the background the app downloads a year of history for
your province (about 40 minutes) and the forecast appears once it has enough data.

The container runs as user `1000:1000` and writes to `./data`. If your user is different,
change the `user:` line in `docker-compose.yml` to what `id -u` says.

To update: `git pull && docker compose up -d --build`.

### Configuration

Everything else is changed from **Settings**. The container takes a few variables:

| Variable | What for | Default |
|---|---|---|
| `TZ` | time zone (the morning summary uses it) | `Europe/Madrid` |
| `PROVINCIAS` | starting province(s), [INE codes](https://www.ine.es/daco/daco42/codmun/cod_provincia.htm) such as `28` or `28,45` | none: chosen in Settings |
| `TELEGRAM_TOKEN`, `TELEGRAM_CHAT` | Telegram alerts | off |
| `APP_URL` | link added at the end of each alert | none |
| `DATA_DIR` | where `pumpcast.db` lives | `/app/data` |

**Telegram**: create a bot with [@BotFather](https://t.me/BotFather), send it any message and
open `https://api.telegram.org/bot<TOKEN>/getUpdates` to find your chat id.

### Security

- **Don't expose it to the internet.** It listens on `127.0.0.1` on purpose. Reach it through a
  VPN (Tailscale, WireGuard) or a reverse proxy with HTTPS inside your network.
- It has **no user accounts**: it's meant for one household. Anyone who reaches it can change
  the settings.
- It stores no personal data except your home location, in the SQLite file.

## Where the data comes from

| Data | Source |
|---|---|
| Prices, today and past days | [Geoportal de carburantes](https://geoportalgasolineras.es), Spanish Ministry for the Ecological Transition (public REST API) |
| Brent crude | Yahoo Finance (`BZ=F`), falling back to [FRED](https://fred.stlouisfed.org/series/DCOILBRENTEU) |
| EUR/USD | [European Central Bank](https://data.ecb.europa.eu) |
| Address search, map tiles | [OpenStreetMap](https://www.openstreetmap.org/copyright) (Nominatim) |

Yahoo Finance is not an official API and may change; the app then falls back to FRED, which
is a few days behind. The Ministry's server only speaks an old TLS cipher
(AES256-GCM-SHA384), which the app enables for that server alone.

## How it's built

Python 3.12, FastAPI and SQLite, Jinja2 templates, Chart.js and Leaflet (bundled, so it works
offline). Nothing to compile: no npm, no bundler.

```
app/
  main.py        web routes and startup        i18n.py      English and Spanish texts
  minetur.py     Ministry prices               mercado.py   Brent and EUR/USD
  prediccion.py  the 7-day forecast            avisos.py    Telegram alerts
  repo.py        SQL queries                   db.py        schema
  tareas.py      background job: reads, history and alerts
  templates/     pages and service worker      static/      CSS, JS, icons, bundled libraries
tests/           pytest, run inside docker build
scripts/         icons, screenshots with WebKit, Portainer deploy, git hook
```

The code and its comments are in Spanish (it started as a personal project); the interface is
in both languages. **Tests run during `docker build`**: if one fails, no image is produced.

```bash
docker build --target test -t pumpcast-test .                  # tests only
docker build -f scripts/capturas/Dockerfile --target export \
  --output type=local,dest=/tmp/capturas .                        # screenshots at iPhone size
```

Issues and pull requests are welcome, especially new languages: add a block to `app/i18n.py`
and the tests check that no text is missing.

## License

[MIT](LICENSE). Not affiliated with the Spanish Ministry or any fuel brand.

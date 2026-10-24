# Herramienta de desarrollo: arranca la app con datos de ejemplo y le hace capturas
# con WebKit (el motor de Safari) a tamaño de iPhone. Necesita internet para el mapa.
#   docker build -f scripts/capturas/Dockerfile --target export --output type=local,dest=/tmp/capturas .
FROM mcr.microsoft.com/playwright/python:v1.63.0-noble AS capturas
WORKDIR /app
COPY requirements.txt .
RUN pip install --break-system-packages --no-cache-dir -r requirements.txt playwright==1.63.0
COPY app ./app
COPY tests/datos ./tests/datos
COPY scripts/capturas/demo.py scripts/capturas/hacer.py /w/
RUN mkdir -p /demo /out && SIN_TAREAS=1 python /w/demo.py \
    && (DATA_DIR=/demo SIN_TAREAS=1 APP_VERSION=capturas python -m uvicorn app.main:app --port 8000 &) \
    && sleep 4 && python /w/hacer.py

FROM scratch AS export
COPY --from=capturas /out /

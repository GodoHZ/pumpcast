// Service worker: guarda los estáticos y la última versión de cada pantalla, para
// que la app se abra y se pueda consultar sin conexión (sin cobertura, el servidor
// apagado...). Las pantallas siempre se piden primero a la red.
const VERSION = {{ version|tojson }};
const ESTATICOS = "pumpcast-estaticos-" + VERSION;
const PANTALLAS = "pumpcast-pantallas-" + VERSION;
const AVISO = {{ aviso|tojson }};
const LANG = {{ lang|tojson }};
const PRECARGA = [
  "/static/estilo.css?v=" + VERSION,
  "/static/graficas.js?v=" + VERSION,
  "/static/ajustes.js?v=" + VERSION,
  "/static/gps.js?v=" + VERSION,
  "/static/acciones.js?v=" + VERSION,
  "/static/mapa-base.js?v=" + VERSION,
  "/static/instalar.js?v=" + VERSION,
  "/static/fluido.js?v=" + VERSION,
  "/static/vendor/chart.umd.min.js?v=" + VERSION,
  "/static/vendor/leaflet/leaflet.js?v=" + VERSION,
  "/static/vendor/leaflet/leaflet.css?v=" + VERSION,
  "/static/iconos/icono-192.png",
  "/sin-conexion",
];

self.addEventListener("install", (event) => {
  event.waitUntil(caches.open(ESTATICOS).then((c) => c.addAll(PRECARGA)).then(() => self.skipWaiting()));
});

self.addEventListener("activate", (event) => {
  event.waitUntil(
    caches.keys()
      .then((nombres) => Promise.all(nombres.filter((n) => n !== ESTATICOS && n !== PANTALLAS).map((n) => caches.delete(n))))
      .then(() => self.clients.claim())
  );
});

function aviso(fecha) {
  let cuando = "";
  try {
    cuando = new Date(fecha).toLocaleString(LANG === "es" ? "es-ES" : "en-GB",
      { day: "numeric", month: "short", hour: "2-digit", minute: "2-digit" });
  } catch (e) { /* sin fecha */ }
  return '<div class="sin-conexion" role="status">' + AVISO.replace("{fecha}", cuando) + "</div>";
}

async function pantallaGuardada(peticion) {
  const guardada = await caches.match(peticion);
  if (!guardada) return caches.match("/sin-conexion");
  const html = (await guardada.text()).replace("</body>", aviso(guardada.headers.get("date")) + "</body>");
  return new Response(html, { headers: { "Content-Type": "text/html; charset=utf-8", "Cache-Control": "no-store" } });
}

// Pantallas pedidas por adelantado (fluido.js: las de la barra cuando la app está quieta y la que vas
// a tocar al acercar el dedo). Si se abren en menos de 45 s salen al instante, y solo una vez: después
// se vuelven a pedir. Guardar algo (ajustes, favorita, ubicación) las tira, porque pueden haber cambiado.
const ADELANTADAS = new Map();
const VIDA_ADELANTADA = 45000;

self.addEventListener("message", (event) => {
  const pedida = event.data && event.data.adelantar;
  if (typeof pedida !== "string") return;
  const url = new URL(pedida, self.location.origin);
  if (url.origin !== self.location.origin || url.pathname.startsWith("/admin")) return;
  const previa = ADELANTADAS.get(url.href);
  if (previa && Date.now() - previa.cuando < VIDA_ADELANTADA / 3) return;     // ya está fresca
  const respuesta = fetch(url.href, { credentials: "same-origin" })
    .then((res) => (res.ok && (res.headers.get("Content-Type") || "").includes("text/html") ? res : null))
    .catch(() => null);
  ADELANTADAS.set(url.href, { cuando: Date.now(), respuesta });
  event.waitUntil(respuesta);
});

self.addEventListener("fetch", (event) => {
  const peticion = event.request;
  if (peticion.method !== "GET") {                      // guardar ajustes, actualizar... siempre a la red
    ADELANTADAS.clear();
    return;
  }
  const url = new URL(peticion.url);
  if (url.origin !== self.location.origin) return;      // el mapa de OpenStreetMap, a su aire
  if (url.pathname.startsWith("/admin")) return;        // el panel nunca se guarda en el móvil

  const adelantada = peticion.mode === "navigate" && ADELANTADAS.get(url.href);
  if (adelantada) {
    ADELANTADAS.delete(url.href);
    if (Date.now() - adelantada.cuando < VIDA_ADELANTADA) {
      event.respondWith(adelantada.respuesta.then((res) => res || fetch(peticion)));
      return;
    }
  }

  if (url.pathname.startsWith("/static/")) {
    event.respondWith(caches.match(peticion).then((hay) => hay || fetch(peticion).then((res) => {
      const copia = res.clone();
      caches.open(ESTATICOS).then((c) => c.put(peticion, copia));
      return res;
    })));
    return;
  }

  if (peticion.mode === "navigate") {
    event.respondWith(fetch(peticion).then((res) => {
      // Lo marcado «no-store» (/pasar lleva tus datos; /ir, tu posición) no se guarda en el móvil.
      if (res.ok && (res.headers.get("Content-Type") || "").includes("text/html")
          && !(res.headers.get("Cache-Control") || "").includes("no-store")) {
        const copia = res.clone();
        caches.open(PANTALLAS).then((c) => c.put(peticion, copia));
      }
      return res;
    }).catch(() => pantallaGuardada(peticion)));
  }
});

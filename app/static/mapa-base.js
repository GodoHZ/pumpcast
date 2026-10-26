// El fondo de los mapas: OpenFreeMap (mapas vectoriales, gratis y sin límites para webs como
// esta), claro u oscuro como el resto de la app. Sin WebGL, las teselas de OpenStreetMap de toda la vida.
function fondoMapa(mapa) {
  const datos = '© <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>';
  const canvas = document.createElement("canvas");
  const webgl = window.maplibregl && L.maplibreGL && (canvas.getContext("webgl2") || canvas.getContext("webgl"));
  if (!webgl) {
    return L.tileLayer("https://tile.openstreetmap.org/{z}/{x}/{y}.png", { maxZoom: 19, attribution: datos }).addTo(mapa);
  }
  maplibregl.setWorkerUrl("/static/vendor/maplibre/maplibre-gl-csp-worker.js");
  const tema = document.documentElement.dataset.theme;
  const oscuro = tema ? tema === "dark" : matchMedia("(prefers-color-scheme: dark)").matches;
  return L.maplibreGL({
    style: `https://tiles.openfreemap.org/styles/${oscuro ? "dark" : "positron"}`,
    attribution: '<a href="https://openfreemap.org">OpenFreeMap</a> · © <a href="https://www.openmaptiles.org/">OpenMapTiles</a> · ' + datos,
  }).addTo(mapa);
}

// Ajustes: colocar la casa buscando la dirección, tocando el mapa, arrastrando la
// chincheta o con el GPS. Necesita Leaflet cargado antes y window.I18N.
(() => {
  const $ = (id) => document.getElementById(id);
  const { t } = window.I18N;
  const estado = $("ubicacion-estado");
  const numero = (texto) => parseFloat(String(texto).replace(",", "."));
  const inicio = [numero($("lat").value), numero($("lon").value)];

  const mapa = L.map("mapa-casa").setView(inicio, 14);
  L.tileLayer("https://tile.openstreetmap.org/{z}/{x}/{y}.png", { maxZoom: 19, attribution: "© OpenStreetMap" }).addTo(mapa);
  const chincheta = L.marker(inicio, { draggable: true, autoPan: true }).addTo(mapa);
  const circulo = L.circle(inicio, { radius: numero($("radio").value) * 1000, color: "#0f766e", weight: 1, fillOpacity: 0.05 }).addTo(mapa);

  function poner(lat, lon, mensaje, centrar) {
    $("lat").value = lat.toFixed(5);
    $("lon").value = lon.toFixed(5);
    chincheta.setLatLng([lat, lon]);
    circulo.setLatLng([lat, lon]);
    if (centrar) mapa.setView([lat, lon], 16);
    estado.textContent = mensaje + t.guardar;
  }

  // Al elegir una dirección, su provincia pasa a ser la de los precios.
  function elegirProvincia(codigo) {
    const lista = $("provincias");
    const opcion = codigo && lista.querySelector(`option[value="${codigo}"]`);
    if (!opcion) return "";
    for (const o of lista.options) o.selected = o === opcion;
    opcion.scrollIntoView({ block: "nearest" });
    return t.provincia.replace("{p}", opcion.textContent);
  }

  chincheta.on("dragend", () => { const p = chincheta.getLatLng(); poner(p.lat, p.lng, t.movida); });
  mapa.on("click", (e) => poner(e.latlng.lat, e.latlng.lng, t.tocado));
  $("radio").addEventListener("input", () => { const r = numero($("radio").value); if (r > 0) circulo.setRadius(r * 1000); });
  for (const id of ["lat", "lon"]) {
    $(id).addEventListener("change", () => {
      const lat = numero($("lat").value), lon = numero($("lon").value);
      if (!isNaN(lat) && !isNaN(lon)) poner(lat, lon, t.coordenadas, true);
    });
  }

  async function buscar() {
    const q = $("buscar").value.trim();
    const lista = $("resultados");
    lista.replaceChildren();
    if (q.length < 3) { estado.textContent = t.escribe_mas; return; }
    estado.textContent = t.buscando;
    try {
      const r = await fetch("/api/buscar?q=" + encodeURIComponent(q));
      if (!r.ok) throw new Error((await r.json()).detail || r.status);
      const { resultados } = await r.json();
      if (!resultados.length) { estado.textContent = t.no_encontrada; return; }
      estado.textContent = t.elige;
      for (const res of resultados) {
        const li = document.createElement("li");
        const boton = document.createElement("button");
        boton.type = "button";
        boton.textContent = res.nombre;
        boton.addEventListener("click", () => {
          lista.replaceChildren();
          poner(res.lat, res.lon, t.encontrada + elegirProvincia(res.provincia), true);
        });
        li.append(boton);
        lista.append(li);
      }
    } catch (e) {
      estado.textContent = t.no_se_pudo_buscar + e.message;
    }
  }
  $("buscar-boton").addEventListener("click", buscar);
  $("buscar").addEventListener("keydown", (e) => { if (e.key === "Enter") { e.preventDefault(); buscar(); } });

  $("ubicacion").addEventListener("click", () => {
    if (!navigator.geolocation) { estado.textContent = t.sin_gps; return; }
    estado.textContent = t.buscando_gps;
    navigator.geolocation.getCurrentPosition(
      (pos) => poner(pos.coords.latitude, pos.coords.longitude, t.gps_ok, true),
      (err) => { estado.textContent = t.no_se_pudo + err.message; },
      { enableHighAccuracy: true, timeout: 15000 });
  });
})();

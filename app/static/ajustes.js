// Ajustes: colocar la ubicación buscando la dirección, tocando el mapa, arrastrando la
// chincheta o con el GPS. Necesita Leaflet cargado antes y window.I18N.
//
// La dirección se busca en OpenStreetMap (Nominatim) directamente desde el navegador: no pasa
// por el servidor de Pumpcast, que así ni la ve ni carga con las búsquedas de todo el mundo.
(() => {
  const $ = (id) => document.getElementById(id);
  const { t, lang } = window.I18N;
  const estado = $("ubicacion-estado");
  const numero = (texto) => parseFloat(String(texto).replace(",", "."));
  const lat0 = numero($("lat").value), lon0 = numero($("lon").value);
  const hayUbicacion = !isNaN(lat0) && !isNaN(lon0);
  const inicio = hayUbicacion ? [lat0, lon0] : [40.2, -3.6];          // sin ubicación: toda España

  const mapa = L.map("mapa-casa").setView(inicio, hayUbicacion ? 14 : 5);
  L.tileLayer("https://tile.openstreetmap.org/{z}/{x}/{y}.png", { maxZoom: 19, attribution: '© <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>' }).addTo(mapa);
  const chincheta = L.marker(inicio, { draggable: true, autoPan: true });
  const circulo = L.circle(inicio, { radius: numero($("radio").value) * 1000, color: "#0f766e", weight: 1, fillOpacity: 0.05 });
  if (hayUbicacion) { chincheta.addTo(mapa); circulo.addTo(mapa); }

  function poner(lat, lon, mensaje, centrar) {
    if (!mapa.hasLayer(chincheta)) { chincheta.addTo(mapa); circulo.addTo(mapa); }
    $("lat").value = lat.toFixed(5);
    $("lon").value = lon.toFixed(5);
    chincheta.setLatLng([lat, lon]);
    circulo.setLatLng([lat, lon]);
    if (centrar) mapa.setView([lat, lon], 16);
    estado.textContent = mensaje + t.guardar;
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
      const url = "https://nominatim.openstreetmap.org/search?" + new URLSearchParams(
        { q, format: "jsonv2", limit: "5", countrycodes: "es", "accept-language": lang });
      const r = await fetch(url);
      if (!r.ok) throw new Error(r.status);
      const resultados = (await r.json()).map((d) => ({ nombre: d.display_name, lat: parseFloat(d.lat), lon: parseFloat(d.lon) }));
      if (!resultados.length) { estado.textContent = t.no_encontrada; return; }
      estado.textContent = t.elige + " " + t.fuente_busqueda;
      for (const res of resultados) {
        const li = document.createElement("li");
        const boton = document.createElement("button");
        boton.type = "button";
        boton.textContent = res.nombre;
        boton.addEventListener("click", () => {
          lista.replaceChildren();
          poner(res.lat, res.lon, t.encontrada, true);
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

  $("formulario").addEventListener("submit", (e) => {
    if (isNaN(numero($("lat").value)) || isNaN(numero($("lon").value))) {
      e.preventDefault();
      estado.textContent = t.falta_ubicacion;
      estado.scrollIntoView({ block: "center" });
    }
  });

  // Al activar «usar dónde estoy» sin ubicación elegida, la primera la da el GPS.
  $("gps")?.addEventListener("change", (e) => {
    if (e.target.checked && isNaN(numero($("lat").value))) $("ubicacion").click();
  });

  $("ubicacion").addEventListener("click", () => {
    if (!navigator.geolocation) { estado.textContent = t.sin_gps; return; }
    estado.textContent = t.buscando_gps;
    navigator.geolocation.getCurrentPosition(
      (pos) => poner(pos.coords.latitude, pos.coords.longitude, t.gps_ok, true),
      (err) => { estado.textContent = t.no_se_pudo + err.message; },
      { enableHighAccuracy: true, timeout: 15000 });
  });
})();

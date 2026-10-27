// /ir sin posición: la pide al navegador y vuelve a /ir con ella (redondeada a unos 100 m), que
// ya abre la app de mapas camino de la mejor gasolinera de alrededor.
(() => {
  const estado = document.getElementById("ir-estado");
  if (!navigator.geolocation) { estado.textContent = estado.dataset.sinGps; return; }
  navigator.geolocation.getCurrentPosition(
    (pos) => {
      const p = new URLSearchParams(location.search);
      p.set("lat", pos.coords.latitude.toFixed(3));
      p.set("lon", pos.coords.longitude.toFixed(3));
      location.replace("/ir?" + p);
    },
    (err) => { estado.textContent = estado.dataset.error + err.message; },
    { enableHighAccuracy: false, timeout: 15000, maximumAge: 60000 });
})();

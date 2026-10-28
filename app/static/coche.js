// Modo coche: busca desde donde estás (redondeado a unos 100 m, como /ir) y vuelve a buscar cada
// minuto si te has movido más de un kilómetro. La pantalla no se apaga mientras está abierto.
(() => {
  const { aqui, buscando } = window.COCHE;
  const KM_PARA_RECARGAR = 1;
  const CADA = 60 * 1000;
  const donde = document.getElementById("coche-donde");
  const textoInicial = donde.textContent;
  const url = new URL(location.href);

  // Que no se apague la pantalla (Wake Lock; donde no lo hay, se apaga como siempre).
  async function despierta() {
    try { await navigator.wakeLock?.request("screen"); } catch (e) { /* sin permiso o sin batería */ }
  }
  despierta();
  document.addEventListener("visibilitychange", () => { if (document.visibilityState === "visible") despierta(); });

  function km(lat1, lon1, lat2, lon2) {
    const r = Math.PI / 180;
    const a = Math.sin((lat2 - lat1) * r / 2) ** 2
      + Math.cos(lat1 * r) * Math.cos(lat2 * r) * Math.sin((lon2 - lon1) * r / 2) ** 2;
    return 12742 * Math.asin(Math.sqrt(a));
  }

  function buscar(forzar) {
    if (!navigator.geolocation) return;
    if (!aqui || forzar) donde.textContent = buscando;
    navigator.geolocation.getCurrentPosition((pos) => {
      const { latitude: lat, longitude: lon } = pos.coords;
      const antes = [parseFloat(url.searchParams.get("lat")), parseFloat(url.searchParams.get("lon"))];
      if (forzar || !aqui || km(antes[0], antes[1], lat, lon) > KM_PARA_RECARGAR) {
        url.searchParams.set("lat", lat.toFixed(3));
        url.searchParams.set("lon", lon.toFixed(3));
        location.replace(url);
      }
    }, () => { donde.textContent = textoInicial; }, { timeout: 15000, maximumAge: 30000 });
  }

  buscar(false);
  setInterval(() => buscar(false), CADA);
  document.getElementById("coche-actualizar").addEventListener("click", () => buscar(true));
})();

// «Usar dónde estoy»: al abrir una página pide la posición una vez (no te sigue) y, si te has
// movido más de 1 km, la manda al servidor, que solo cambia tu cookie, y recarga.
// La posición sale ya redondeada a 3 decimales (~100 m). Necesita window.I18N.
(() => {
  const estado = document.getElementById("gps-estado");
  const { t } = window.I18N;
  const avisar = (texto) => { estado.textContent = texto; estado.hidden = false; };
  if (!navigator.geolocation) { avisar(t.gps_ultima); return; }

  navigator.geolocation.getCurrentPosition(async (pos) => {
    const datos = new URLSearchParams({ lat: pos.coords.latitude.toFixed(3), lon: pos.coords.longitude.toFixed(3) });
    try {
      const r = await fetch("/ubicacion", { method: "POST", body: datos });
      const res = await r.json();
      if (res.cambiada) { avisar(t.gps_movido); location.reload(); }
      else if (res.error) avisar(res.error === "err.fuera" ? t.gps_fuera : t.gps_ultima);
    } catch (e) {
      avisar(t.gps_ultima);
    }
  }, () => avisar(t.gps_ultima), { enableHighAccuracy: false, timeout: 10000, maximumAge: 120000 });
})();

// «Usar dónde estoy»: al abrir una página pide la posición una vez (no te sigue) y, si te has
// movido más de 1 km, la manda al servidor, que solo cambia tu cookie, y recarga.
// La posición sale ya redondeada a 3 decimales (~100 m). Necesita window.I18N.
//
// Dentro de un edificio, la posición por wifi o antena puede bailar más de 1 km de una medida a
// otra: sin freno, cada recarga mediría otra vez, recargaría... y la web acabaría diciendo
// «demasiadas peticiones». Por eso no se usan medidas muy imprecisas ni se recarga más de una
// vez cada pocos minutos.
const GPS_PRECISION_MINIMA = 1500;      // metros: con más error que esto, no merece la pena
const GPS_MINUTOS_ENTRE_RECARGAS = 5;
(() => {
  const estado = document.getElementById("gps-estado");
  const { t } = window.I18N;
  const avisar = (texto) => { estado.textContent = texto; estado.hidden = false; };
  if (!navigator.geolocation) { avisar(t.gps_ultima); return; }

  const ultima = () => { try { return Number(sessionStorage.getItem("gps-recarga")) || 0; } catch { return 0; } };
  const apuntar = () => { try { sessionStorage.setItem("gps-recarga", String(Date.now())); } catch { /* sin almacenamiento */ } };
  if (Date.now() - ultima() < GPS_MINUTOS_ENTRE_RECARGAS * 60000) return;

  navigator.geolocation.getCurrentPosition(async (pos) => {
    if (pos.coords.accuracy > GPS_PRECISION_MINIMA) { avisar(t.gps_ultima); return; }
    const datos = new URLSearchParams({ lat: pos.coords.latitude.toFixed(3), lon: pos.coords.longitude.toFixed(3) });
    try {
      const r = await fetch("/ubicacion", { method: "POST", body: datos });
      const res = await r.json();
      if (res.cambiada) { avisar(t.gps_movido); apuntar(); location.reload(); }
      else if (res.error) avisar(res.error === "err.fuera" ? t.gps_fuera : t.gps_ultima);
    } catch (e) {
      avisar(t.gps_ultima);
    }
  }, () => avisar(t.gps_ultima), { enableHighAccuracy: false, timeout: 10000, maximumAge: 120000 });
})();

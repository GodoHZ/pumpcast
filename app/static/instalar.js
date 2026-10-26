// «Instálala como una app». En Android/Chrome, el navegador deja instalarla con un botón; en el
// iPhone, Apple no lo permite a ninguna web, así que se explican los dos toques que hacen falta.
// Sale una vez, la primera vez que se ve algo útil (con ubicación ya elegida), y no vuelve si se
// cierra; desde Ajustes se puede abrir otra vez.
(() => {
  const hoja = document.getElementById("instalar");
  if (!hoja) return;
  const instalada = matchMedia("(display-mode: standalone)").matches || navigator.standalone === true;
  const ua = navigator.userAgent;
  const ios = /iPhone|iPad|iPod/.test(ua) || (/Macintosh/.test(ua) && navigator.maxTouchPoints > 1);
  const dentroDeOtraApp = /FBAN|FBAV|Instagram|Line\/|TikTok|Twitter/.test(ua);     // no pueden instalar nada
  const visto = () => { try { return localStorage.getItem("instalar-visto"); } catch { return "1"; } };
  const apuntar = () => { try { localStorage.setItem("instalar-visto", "1"); } catch { /* sin almacenamiento */ } };
  let aviso = null;                                       // Android: el permiso para instalar de verdad
  const boton = document.getElementById("instalar-abrir");  // en Ajustes, para quien la cerró y luego quiere

  const abrir = () => {
    // Con el permiso de Android basta el botón; si no, los pasos del iPhone o los del menú del navegador.
    hoja.querySelector("[data-ios]").hidden = Boolean(aviso) || !ios || dentroDeOtraApp;
    hoja.querySelector("[data-otro]").hidden = Boolean(aviso) || ios || dentroDeOtraApp;
    hoja.querySelector("[data-otra-app]").hidden = !dentroDeOtraApp;
    hoja.querySelector("[data-instalar]").hidden = !aviso;
    hoja.hidden = false;
  };
  const cerrar = () => { hoja.hidden = true; apuntar(); };
  hoja.querySelectorAll("[data-cerrar]").forEach((b) => b.addEventListener("click", cerrar));
  hoja.querySelector("[data-instalar]").addEventListener("click", async () => {
    if (!aviso) return;
    aviso.prompt();
    await aviso.userChoice.catch(() => null);
    aviso = null;
    cerrar();
  });

  window.addEventListener("beforeinstallprompt", (e) => {
    e.preventDefault();
    aviso = e;
    if (hoja.dataset.auto !== undefined && !visto()) abrir();
  });

  // En Ajustes: el botón, si aún no está instalada; si ya lo está, decirlo.
  if (boton) boton.hidden = instalada;
  const yaInstalada = document.getElementById("instalada");
  if (yaInstalada) yaInstalada.hidden = !instalada;
  boton?.addEventListener("click", abrir);

  if (!instalada && ios && hoja.dataset.auto !== undefined && !visto()) setTimeout(abrir, 2500);
})();

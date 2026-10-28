// Botones que necesitan algo de JavaScript.
(() => {
  // «Cómo llegar»: pregunta con qué app abrir la ruta, o usa la de Ajustes si hay una elegida.
  // Sin JavaScript, el enlace va a Google Maps.
  // Escucha en captura porque Leaflet corta algunos clics antes de que suban.
  const dialogo = document.getElementById("elegir-mapa");
  if (dialogo && dialogo.showModal) {
    document.addEventListener("click", (evento) => {
      const enlace = evento.target.closest("[data-ir]");
      if (!enlace) return;
      evento.preventDefault();
      const [lat, lon] = enlace.dataset.ir.split(",");
      for (const opcion of dialogo.querySelectorAll("[data-plantilla]")) {
        opcion.href = opcion.dataset.plantilla.replace("{lat}", lat).replace("{lon}", lon);
      }
      const elegida = dialogo.querySelector(`[data-clave="${dialogo.dataset.app}"]`);   // la de Ajustes
      if (elegida) window.open(elegida.href, "_blank", "noopener");
      else dialogo.showModal();
    }, true);
    dialogo.addEventListener("click", (evento) => {
      if (evento.target === dialogo || evento.target.closest("a")) dialogo.close();   // fuera de la hoja, o ya elegida
    });
  }

  // Compartir una gasolinera: el menú del móvil o, si no hay, copiar el enlace.
  for (const boton of document.querySelectorAll("[data-compartir]")) {
    const url = location.origin + location.pathname;
    if (navigator.share) {
      boton.hidden = false;
      boton.addEventListener("click", () => navigator.share({ title: boton.dataset.compartir, url }).catch(() => {}));
    } else if (navigator.clipboard) {
      boton.hidden = false;
      boton.addEventListener("click", async () => {
        await navigator.clipboard.writeText(url);
        boton.lastChild.textContent = " " + window.I18N.t.copiado;
      });
    }
  }

  // Direcciones para pegar (los atajos de Siri): un toque las copia.
  for (const codigo of document.querySelectorAll("[data-copiar]")) {
    if (!navigator.clipboard) break;
    codigo.tabIndex = 0;
    codigo.setAttribute("role", "button");
    const copiar = async () => {
      await navigator.clipboard.writeText(codigo.textContent.trim());
      codigo.dataset.copiado = window.I18N.t.copiado;
      setTimeout(() => delete codigo.dataset.copiado, 1800);
    };
    codigo.addEventListener("click", copiar);
    codigo.addEventListener("keydown", (e) => { if (e.key === "Enter") copiar(); });
  }
})();

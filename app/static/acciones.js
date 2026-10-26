// Botones que necesitan algo de JavaScript.
(() => {
  // «Cómo llegar»: pregunta con qué app abrir la ruta. Sin JavaScript, el enlace va a Google Maps.
  // Escucha en captura porque Leaflet corta los clics de sus ventanitas antes de que suban.
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
      dialogo.showModal();
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
})();

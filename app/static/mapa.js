// El mapa de gasolineras: cada una con la inicial de su marca (no logos) y su precio al lado, del
// color de lo barata o cara que es: de verde a rojo. Se filtra por abiertas, más baratas que la media
// y marcas; los filtros se recuerdan en este navegador. Necesita Leaflet, mapa-base.js y window.MAPA.
(() => {
  const { estaciones, escala, casa, radio, comb, favoritas: favs, textoFavorita, estrella, cts, cerrar, unidad, fuente } = window.MAPA;
  const { t, decimal, europeo } = window.I18N;
  const favoritas = new Set(favs);
  const ZOOM_CON_PRECIO = 13;                 // más lejos, solo el distintivo: si no, no se ve nada
  const CLAVE = "pumpcast_filtros_mapa";

  const mapa = L.map("mapa", { zoomControl: false }).setView(casa, 12);
  fondoMapa(mapa);
  mapa.attributionControl.setPrefix(false).addAttribution(fuente);      // el pie de la página, aquí
  L.circle(casa, { radius: radio * 1000, color: getComputedStyle(document.documentElement).getPropertyValue("--tinta-marca").trim() || "#0f766e", weight: 1.5, dashArray: "4 6", fillOpacity: 0.05 }).addTo(mapa);
  L.circleMarker(casa, { radius: 7, color: "#fff", weight: 2, fillColor: "#2563eb", fillOpacity: 1 })
    .addTo(mapa).bindPopup(t.casa);

  const cifra = (v, d) => v.toFixed(d).replace(".", decimal);
  const precio = (p) => europeo ? `${cifra(p, 3)} €` : `€${cifra(p, 3)}`;
  const km = (d) => d < 1 ? Math.round(d * 1000) + " m" : cifra(d, 1) + " km";
  const color = (p) => {
    const x = escala.max > escala.min ? Math.min(1, Math.max(0, (p - escala.min) / (escala.max - escala.min))) : 0;
    return `hsl(${Math.round(130 * (1 - x))} 70% 38%)`;
  };
  const nombre = (s) => s.toLowerCase().replace(/(^|\s)\S/g, (l) => l.toUpperCase());

  // La ficha de la gasolinera elegida: una hoja que sube desde abajo, como en Mapas del iPhone.
  const hoja = document.getElementById("ficha");
  let elegida = null;
  function ficha(e) {
    hoja.innerHTML = '<span class="asa" aria-hidden="true"></span>'
      + '<div class="ficha-cabeza"><span class="pin-marca"></span><div><b></b><small></small></div>'
      + '<button type="button" class="cerrar-ficha">×</button></div>'
      + '<p class="ficha-precio"><b></b><span class="nota"></span><span class="dif"></span></p>'
      + '<span class="estado"></span>'
      + '<div class="botones"><a class="boton"></a><a class="boton secundario"></a>'
      + '<form method="post"><button class="boton secundario solo-icono"></button></form></div>';
    const distintivo = hoja.querySelector(".pin-marca");
    distintivo.style.setProperty("--f", e.insignia.fondo);
    distintivo.style.setProperty("--t", e.insignia.tinta);
    distintivo.textContent = e.insignia.texto;
    hoja.querySelector(".ficha-cabeza b").textContent = nombre(e.rotulo);
    hoja.querySelector(".ficha-cabeza small").textContent = `${e.municipio} · ${km(e.distancia)}`;
    const x = hoja.querySelector(".cerrar-ficha");
    x.ariaLabel = x.title = cerrar;
    x.addEventListener("click", cerrarFicha);
    hoja.querySelector(".ficha-precio b").textContent = europeo ? cifra(e.precio, 3) : `€${cifra(e.precio, 3)}`;
    hoja.querySelector(".ficha-precio .nota").textContent = europeo ? `€/${unidad}` : `/${unidad}`;
    const dif = (e.precio - escala.media) * 100;
    const marcaDif = hoja.querySelector(".ficha-precio .dif");
    marcaDif.textContent = `${dif > 0 ? "+" : "−"}${cifra(Math.abs(dif), 1)} ${cts}`;
    marcaDif.classList.add(dif > 0 ? "sube" : "baja");
    const horario = hoja.querySelector(".estado");
    horario.textContent = e.horario;
    horario.classList.add(e.abierta === false ? "cerrada" : "abierta");
    const marcada = favoritas.has(e.id);
    const form = hoja.querySelector("form");
    form.action = `/favorita/${e.id}`;
    const fav = form.querySelector("button");
    fav.innerHTML = estrella;
    fav.title = fav.ariaLabel = textoFavorita[marcada ? 1 : 0];
    fav.setAttribute("aria-pressed", marcada);
    fav.classList.toggle("marcada", marcada);
    const [ir, historial] = hoja.querySelectorAll(".botones a");
    ir.textContent = t.como_llegar;
    ir.dataset.ir = `${e.lat},${e.lon}`;
    ir.href = `https://www.google.com/maps/dir/?api=1&destination=${e.lat},${e.lon}`;
    ir.target = "_blank";
    ir.rel = "noopener";
    historial.textContent = t.ver_historial;
    historial.href = `/estacion/${e.id}?c=${comb}`;
  }
  function abrirFicha(p) {
    if (elegida) elegida.marcador.getElement()?.querySelector(".pin")?.classList.remove("elegida");
    elegida = p;
    p.marcador.getElement()?.querySelector(".pin")?.classList.add("elegida");
    ficha(p.e);
    hoja.setAttribute("aria-hidden", "false");
    // Que la gasolinera quede a la vista, por encima de la hoja.
    const alto = hoja.offsetHeight + 90;
    const punto = mapa.latLngToContainerPoint([p.e.lat, p.e.lon]);
    const libre = mapa.getSize().y - alto;
    if (punto.y > libre - 40 || punto.y < 140) mapa.panBy([0, punto.y - (140 + (libre - 140) / 2)]);
  }
  function cerrarFicha() {
    if (elegida) elegida.marcador.getElement()?.querySelector(".pin")?.classList.remove("elegida");
    elegida = null;
    hoja.setAttribute("aria-hidden", "true");
  }
  mapa.on("click", cerrarFicha);
  document.addEventListener("keydown", (ev) => { if (ev.key === "Escape") cerrarFicha(); });
  // Deslizar la hoja hacia abajo la cierra.
  let desde = null;
  hoja.addEventListener("pointerdown", (ev) => { if (!ev.target.closest("a, button")) desde = ev.clientY; });
  hoja.addEventListener("pointermove", (ev) => {
    if (desde === null) return;
    hoja.style.transform = `translateY(${Math.max(0, ev.clientY - desde)}px)`;
  });
  const soltar = (ev) => {
    if (desde === null) return;
    const bajada = ev.clientY - desde;
    desde = null;
    hoja.style.transform = "";
    if (bajada > 60) cerrarFicha();
  };
  hoja.addEventListener("pointerup", soltar);
  hoja.addEventListener("pointercancel", soltar);

  function icono(e) {
    const pin = document.createElement("div");
    pin.className = "pin";
    pin.classList.toggle("cerrada", e.abierta === false);
    pin.classList.toggle("fav", favoritas.has(e.id));
    pin.style.setProperty("--f", e.insignia.fondo);
    pin.style.setProperty("--t", e.insignia.tinta);
    pin.style.setProperty("--p", color(e.precio));
    const marca = document.createElement("span");
    marca.className = "pin-marca";
    marca.textContent = e.insignia.texto;
    const cuanto = document.createElement("span");
    cuanto.className = "pin-precio";
    cuanto.textContent = cifra(e.precio, 3);
    pin.append(marca, cuanto);
    return L.divIcon({ html: pin, className: "pin-icono", iconSize: [28, 28], iconAnchor: [14, 14], popupAnchor: [0, -12] });
  }

  const capa = L.layerGroup().addTo(mapa);
  const puntos = estaciones.map((e) => ({
    e,
    // Las baratas encima de las caras cuando se solapan.
    marcador: L.marker([e.lat, e.lon], { icon: icono(e), title: `${nombre(e.rotulo)} · ${precio(e.precio)}`,
                                         zIndexOffset: Math.round((escala.max - e.precio) * 1000) }),
  }));
  for (const p of puntos) p.marcador.on("click", () => abrirFicha(p));

  const cuerpo = document.getElementById("mapa");
  const zoom = () => cuerpo.classList.toggle("lejos", mapa.getZoom() < ZOOM_CON_PRECIO);
  mapa.on("zoomend", zoom);
  zoom();

  // --- Filtros ---------------------------------------------------------------------------
  let filtros = { abiertas: false, baratas: false, ocultas: [] };     // ocultas: así las marcas nuevas salen
  try { filtros = { ...filtros, ...JSON.parse(localStorage.getItem(CLAVE) || "{}") }; } catch (e) { /* sin guardar */ }
  const guardar = () => { try { localStorage.setItem(CLAVE, JSON.stringify(filtros)); } catch (e) { /* modo privado */ } };

  const marcas = new Map();                   // marca -> {insignia, n}
  for (const { e } of puntos) {
    const m = marcas.get(e.insignia.marca) || { insignia: e.insignia, n: 0 };
    m.n += 1;
    marcas.set(e.insignia.marca, m);
  }

  function aplicar() {
    const ocultas = new Set(filtros.ocultas);
    let vistas = 0;
    for (const { e, marcador } of puntos) {
      const ver = !(filtros.abiertas && e.abierta === false) && !(filtros.baratas && e.precio > escala.media)
        && !ocultas.has(e.insignia.marca);
      if (ver) vistas += 1;
      if (ver && !capa.hasLayer(marcador)) capa.addLayer(marcador);
      if (!ver && capa.hasLayer(marcador)) capa.removeLayer(marcador);
    }
    for (const boton of document.querySelectorAll("[data-filtro]")) {
      boton.setAttribute("aria-pressed", Boolean(filtros[boton.dataset.filtro]));
    }
    const escondidas = [...marcas.keys()].filter((m) => ocultas.has(m)).length;
    document.getElementById("filtro-marcas").setAttribute("aria-pressed", escondidas > 0);
    document.getElementById("filtro-marcas-n").textContent = escondidas ? ` · ${marcas.size - escondidas}/${marcas.size}` : "";
    document.getElementById("filtro-cuenta").textContent = vistas < puntos.length
      ? t.filtro_cuenta.replace("{n}", vistas).replace("{total}", puntos.length) : "";
    guardar();
  }

  for (const boton of document.querySelectorAll("[data-filtro]")) {
    boton.addEventListener("click", () => {
      filtros[boton.dataset.filtro] = !filtros[boton.dataset.filtro];
      aplicar();
    });
  }

  // La hoja de marcas: las de este mapa, de la que más gasolineras tiene a la que menos.
  const dialogo = document.getElementById("elegir-marcas");
  const lista = document.getElementById("lista-marcas");
  function pintarMarcas() {
    const ocultas = new Set(filtros.ocultas);
    lista.replaceChildren();
    for (const [marca, { insignia, n }] of [...marcas].sort((a, b) => b[1].n - a[1].n || a[0].localeCompare(b[0]))) {
      const fila = document.createElement("label");
      fila.className = "fila-marca";
      const casilla = document.createElement("input");
      casilla.type = "checkbox";
      casilla.checked = !ocultas.has(marca);
      casilla.addEventListener("change", () => {
        filtros.ocultas = casilla.checked ? filtros.ocultas.filter((m) => m !== marca) : [...filtros.ocultas, marca];
        aplicar();
      });
      const distintivo = document.createElement("span");
      distintivo.className = "pin-marca";
      distintivo.style.setProperty("--f", insignia.fondo);
      distintivo.style.setProperty("--t", insignia.tinta);
      distintivo.textContent = insignia.texto;
      const texto = document.createElement("span");
      texto.textContent = nombre(marca);
      const cuantas = document.createElement("small");
      cuantas.textContent = n;
      fila.append(casilla, distintivo, texto, cuantas);
      lista.append(fila);
    }
  }
  document.getElementById("filtro-marcas").addEventListener("click", () => { pintarMarcas(); dialogo.showModal(); });
  document.getElementById("marcas-todas").addEventListener("click", () => {
    filtros.ocultas = filtros.ocultas.filter((m) => !marcas.has(m));
    pintarMarcas(); aplicar();
  });
  document.getElementById("marcas-ninguna").addEventListener("click", () => {
    filtros.ocultas = [...new Set([...filtros.ocultas, ...marcas.keys()])];
    pintarMarcas(); aplicar();
  });
  dialogo.addEventListener("click", (e) => { if (e.target === dialogo) dialogo.close(); });

  aplicar();
})();

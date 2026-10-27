// El mapa de gasolineras: cada una con el distintivo de su marca (iniciales y color, no logos) y su
// precio al lado, de verde (barata) a rojo (cara). Se filtra por abiertas, más baratas que la media
// y marcas; los filtros se recuerdan en este navegador. Necesita Leaflet, mapa-base.js y window.MAPA.
(() => {
  const { estaciones, escala, casa, radio, comb, favoritas: favs, textoFavorita, estrella } = window.MAPA;
  const { t, decimal, europeo } = window.I18N;
  const favoritas = new Set(favs);
  const ZOOM_CON_PRECIO = 13;                 // más lejos, solo el distintivo: si no, no se ve nada
  const CLAVE = "pumpcast_filtros_mapa";

  const mapa = L.map("mapa", { zoomControl: false }).setView(casa, 12);
  fondoMapa(mapa);
  L.circle(casa, { radius: radio * 1000, color: "#0f766e", weight: 1, fillOpacity: 0.04 }).addTo(mapa);
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

  function ventanita(e) {
    const popup = document.createElement("div");
    popup.className = "ventanita";
    popup.innerHTML = '<b></b><br><span></span><br><span class="estado"></span>'
      + '<div class="botones"><a class="boton"></a><a class="boton secundario"></a>'
      + '<form method="post"><button class="boton secundario solo-icono"></button></form></div>';
    popup.querySelector("b").textContent = `${precio(e.precio)} · ${nombre(e.rotulo)}`;
    popup.querySelector("span").textContent = `${e.municipio} · ${km(e.distancia)}`;
    const horario = popup.querySelector(".estado");
    horario.textContent = e.horario;
    horario.classList.add(e.abierta === false ? "cerrada" : "abierta");
    const marcada = favoritas.has(e.id);
    const form = popup.querySelector("form");
    form.action = `/favorita/${e.id}`;
    const fav = form.querySelector("button");
    fav.innerHTML = estrella;
    fav.title = fav.ariaLabel = textoFavorita[marcada ? 1 : 0];
    fav.setAttribute("aria-pressed", marcada);
    fav.classList.toggle("marcada", marcada);
    const [ir, historial] = popup.querySelectorAll("a");
    ir.textContent = t.como_llegar;
    ir.dataset.ir = `${e.lat},${e.lon}`;
    ir.href = `https://www.google.com/maps/dir/?api=1&destination=${e.lat},${e.lon}`;
    ir.target = "_blank";
    ir.rel = "noopener";
    historial.textContent = t.ver_historial;
    historial.href = `/estacion/${e.id}?c=${comb}`;
    return popup;
  }

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
                                         zIndexOffset: Math.round((escala.max - e.precio) * 1000) })
      .bindPopup(ventanita(e)),
  }));

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

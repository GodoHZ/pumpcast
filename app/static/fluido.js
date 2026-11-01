// Que cambiar de pantalla se sienta inmediato, como en una app:
// - Las pantallas de la barra se piden por adelantado cuando la app está quieta, y la que vas a tocar,
//   en cuanto acercas el dedo; el service worker las guarda 45 s y las sirve al instante.
// - Al tocar la barra o el orden, la lente se desliza ya, sin esperar a que llegue la página.
// - Lo que se toca responde al dedo (se hunde un poco y se ilumina donde lo pisas).
// - Al bajar, la barra se encoge; al subir, vuelve.
// - En Chrome y Edge, el canto de la barra dobla lo que pasa por debajo, como un cristal de verdad.
(() => {
  const yaPedidas = new Set();
  const adelantar = (enlace) => {
    const sw = navigator.serviceWorker && navigator.serviceWorker.controller;
    if (!sw || !enlace || enlace.target === "_blank" || enlace.hasAttribute("data-ir") || enlace.hasAttribute("download")) return;
    const url = new URL(enlace.href, location.href);
    if (url.origin !== location.origin || url.pathname.startsWith("/admin") || url.hash) return;
    if (url.pathname === location.pathname && url.search === location.search) return;
    if (yaPedidas.has(url.href)) return;
    yaPedidas.add(url.href);
    sw.postMessage({ adelantar: url.href });
  };

  // Con la app quieta: las otras pantallas de la barra (el mapa no: pesa mucho)
  const enReposo = window.requestIdleCallback || ((f) => setTimeout(f, 1200));
  addEventListener("load", () => enReposo(() => {
    for (const a of document.querySelectorAll(".barra a:not([aria-current])")) {
      if (!new URL(a.href).pathname.startsWith("/mapa")) adelantar(a);
    }
  }));

  // Al acercar el dedo (o el ratón)
  const intencion = (evento) => { const a = evento.target.closest && evento.target.closest("a[href]"); if (a) adelantar(a); };
  addEventListener("touchstart", intencion, { passive: true });
  addEventListener("pointerdown", intencion);
  addEventListener("mouseover", (evento) => {
    const a = evento.target.closest && evento.target.closest("a[href]");
    if (!a) return;
    const t = setTimeout(() => adelantar(a), 70);
    a.addEventListener("mouseleave", () => clearTimeout(t), { once: true });
  });

  // La lente se va ya a lo que tocas
  const PULSABLE = ".boton, .barra a, .segmentos a, .chip, .selector-comb, .pastillas a, .boton-coche, .boton-redondo, .opcion span, .lista a";
  const soltar = () => {
    for (const el of document.querySelectorAll(".yendo")) el.classList.remove("yendo");
    for (const el of document.querySelectorAll("[data-yendo]")) delete el.dataset.yendo;
  };
  addEventListener("pointerdown", (evento) => {
    if (evento.button) return;
    const destino = evento.target.closest(".barra a, .segmentos a");
    if (destino && !destino.matches("[aria-current], .activa")) {
      soltar();
      destino.classList.add("yendo");
      destino.parentElement.dataset.yendo = "";
    }
    const pulsado = evento.target.closest(PULSABLE);
    if (!pulsado) return;
    const r = pulsado.getBoundingClientRect();
    pulsado.style.setProperty("--mx", (evento.clientX - r.left) + "px");
    pulsado.style.setProperty("--my", (evento.clientY - r.top) + "px");
    pulsado.classList.add("pulsado");
    const fuera = () => { pulsado.classList.remove("pulsado"); removeEventListener("pointerup", fuera); removeEventListener("pointercancel", fuera); };
    addEventListener("pointerup", fuera);
    addEventListener("pointercancel", fuera);
  });
  // Si al final no se navega (se arrastró, se canceló) o se vuelve atrás, la lente regresa a su sitio
  addEventListener("pointercancel", soltar);
  addEventListener("pageshow", soltar);
  addEventListener("click", (evento) => {
    const a = evento.target.closest(".barra a, .segmentos a");
    if (!a || evento.defaultPrevented) setTimeout(soltar, 0);
  });

  // La barra se encoge al bajar y vuelve al subir (en el móvil)
  const raiz = document.documentElement;
  let ultimaY = scrollY;
  addEventListener("scroll", () => {
    const y = scrollY, dy = y - ultimaY;
    if (Math.abs(dy) < 6) return;
    raiz.classList.toggle("barra-mini", dy > 0 && y > 160);
    ultimaY = y;
  }, { passive: true });

  // Refracción del canto (solo Chrome/Edge: Safari acepta el filtro pero no lo pinta)
  const ua = navigator.userAgent;
  const conLente = !!window.chrome && /Chrome\/\d+/.test(ua) && !/CriOS|FxiOS|EdgiOS/.test(ua)
    && CSS.supports("backdrop-filter", "url(#a)") && !matchMedia("(prefers-reduced-transparency: reduce)").matches;
  if (!conLente || !window.ResizeObserver) return;
  const NS = "http://www.w3.org/2000/svg";
  const svg = document.createElementNS(NS, "svg");
  svg.setAttribute("width", "0"); svg.setAttribute("height", "0"); svg.setAttribute("aria-hidden", "true");
  svg.style.position = "absolute";
  document.body.appendChild(svg);
  let n = 0;
  // Mapa de desplazamiento de un rectángulo redondeado: solo se dobla una franja junto al borde
  const mapa = (w, h, r, franja) => {
    const lienzo = document.createElement("canvas"); lienzo.width = w; lienzo.height = h;
    const ctx = lienzo.getContext("2d"), img = ctx.createImageData(w, h), px = img.data, hx = w / 2, hy = h / 2;
    for (let j = 0; j < h; j++) for (let i = 0; i < w; i++) {
      const X = i + .5 - hx, Y = j + .5 - hy, qx = Math.abs(X) - (hx - r), qy = Math.abs(Y) - (hy - r);
      let dist, nx, ny;
      if (qx > 0 && qy > 0) { const l = Math.hypot(qx, qy); dist = l - r; nx = qx / l * Math.sign(X); ny = qy / l * Math.sign(Y); }
      else if (qx > qy) { dist = qx - r; nx = Math.sign(X); ny = 0; }
      else { dist = qy - r; nx = 0; ny = Math.sign(Y); }
      let m = 0;
      if (-dist >= 0 && -dist < franja) { const t = 1 + dist / franja; m = t * t; }
      const k = (j * w + i) * 4;
      px[k] = 128 - nx * m * 127; px[k + 1] = 128 - ny * m * 127; px[k + 2] = 128; px[k + 3] = 255;
    }
    ctx.putImageData(img, 0, 0);
    return lienzo.toDataURL();
  };
  const refractar = (el) => {
    const w = Math.round(el.offsetWidth), h = Math.round(el.offsetHeight);
    if (!w || !h) return;
    const r = Math.min(w / 2, h / 2, parseFloat(getComputedStyle(el).borderTopLeftRadius) || h / 2);
    const id = "lente-cristal-" + (++n);
    const filtro = document.createElementNS(NS, "filter");
    filtro.setAttribute("id", id); filtro.setAttribute("filterUnits", "userSpaceOnUse");
    filtro.setAttribute("color-interpolation-filters", "sRGB");
    filtro.setAttribute("x", "0"); filtro.setAttribute("y", "0"); filtro.setAttribute("width", w); filtro.setAttribute("height", h);
    const imagen = document.createElementNS(NS, "feImage");
    for (const [k, v] of [["href", mapa(w, h, r, Math.min(22, h * .42))], ["x", 0], ["y", 0], ["width", w], ["height", h], ["preserveAspectRatio", "none"], ["result", "m"]]) imagen.setAttribute(k, v);
    const desplazar = document.createElementNS(NS, "feDisplacementMap");
    for (const [k, v] of [["in", "SourceGraphic"], ["in2", "m"], ["scale", Math.min(46, h * .8)], ["xChannelSelector", "R"], ["yChannelSelector", "G"]]) desplazar.setAttribute(k, v);
    filtro.append(imagen, desplazar);
    if (el._filtro) el._filtro.remove();
    svg.appendChild(filtro); el._filtro = filtro;
    el.style.backdropFilter = `blur(5px) url(#${id}) saturate(185%)`;
  };
  const observador = new ResizeObserver((cambios) => {
    for (const c of cambios) { cancelAnimationFrame(c.target._raf); c.target._raf = requestAnimationFrame(() => refractar(c.target)); }
  });
  for (const el of document.querySelectorAll(".barra, .boton-coche")) observador.observe(el);
})();

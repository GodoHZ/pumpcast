// Pasar los ajustes, las favoritas y los repostajes a otro móvil sin cuentas. Todo va en el enlace,
// detrás de «#» (el navegador nunca manda esa parte al servidor), codificado en base64url.
// En el móvil de destino, los ajustes y las favoritas se guardan en sus cookies (POST /pasar) y los
// repostajes, en su almacenamiento local, sumados a los que hubiera.
(() => {
  const $ = (id) => document.getElementById(id);
  const { mios, base, t } = window.PASAR;
  const REPOSTAJES = "pumpcast_repostajes";
  const MAX_QR = 2300;                        // caracteres: más, y el código sale ilegible para la cámara

  const a64 = (texto) => btoa(String.fromCharCode(...new TextEncoder().encode(texto)))
    .replace(/\+/g, "-").replace(/\//g, "_").replace(/=+$/, "");
  const de64 = (texto) => new TextDecoder().decode(
    Uint8Array.from(atob(texto.replace(/-/g, "+").replace(/_/g, "/")), (c) => c.charCodeAt(0)));

  function repostajes() {
    try { return JSON.parse(localStorage.getItem(REPOSTAJES) || "[]"); } catch (e) { return []; }
  }
  // Compactos para que quepan en un QR: [fecha, litros, precio, km, lleno, gasolinera].
  const compactar = (r) => [r.fecha, r.litros, r.precio, r.km ?? null, r.lleno ? 1 : 0, r.estacion || ""];
  const descompactar = ([fecha, litros, precio, km, lleno, estacion]) => ({
    id: `${fecha}-${litros}-${precio}`, fecha, litros, precio, km, lleno: Boolean(lleno), estacion });

  function resumen(d) {
    const partes = [];
    if (d.p) partes.push(t.ajustes);
    if (d.f && d.f.length) partes.push(t.favoritas.replace("{n}", d.f.length));
    if (d.r && d.r.length) partes.push(t.repostajes.replace("{n}", d.r.length));
    return partes.length > 1 ? partes.slice(0, -1).join(", ") + t.y + partes.at(-1) : partes[0] || "";
  }

  // --- Llega de otro móvil -------------------------------------------------------------------
  if (location.hash.length > 1) {
    $("pasar-llevar").hidden = true;
    $("pasar-traer").hidden = false;
    let datos = null;
    try {
      datos = JSON.parse(de64(location.hash.slice(1)));
      if (datos.v !== 1) throw new Error("versión");
    } catch (e) {
      datos = null;
    }
    const estado = $("pasar-estado");
    if (!datos || !resumen(datos)) {
      estado.textContent = t.mal;
      estado.className = "mensaje error";
      estado.hidden = false;
      $("pasar-importar").hidden = true;
      return;
    }
    $("pasar-trae").textContent = resumen(datos) + ".";
    $("pasar-importar").addEventListener("click", async () => {
      try {
        if (datos.p || (datos.f && datos.f.length)) {
          const r = await fetch("/pasar", { method: "POST", headers: { "Content-Type": "application/json" },
                                            body: JSON.stringify({ p: datos.p, f: datos.f }) });
          if (!r.ok) throw new Error(r.status);
        }
        if (datos.r && datos.r.length) {
          const ya = repostajes();
          const hay = new Set(ya.map((r) => `${r.fecha}-${r.litros}-${r.precio}`));
          const nuevos = datos.r.map(descompactar).filter((r) => !hay.has(r.id));
          try { localStorage.setItem(REPOSTAJES, JSON.stringify([...ya, ...nuevos])); } catch (e) { /* modo privado */ }
        }
        history.replaceState(null, "", location.pathname);         // que el enlace no se quede a la vista
        estado.textContent = t.importado;
        estado.className = "mensaje ok";
        $("pasar-importar").hidden = true;
        $("pasar-inicio").hidden = false;
      } catch (e) {
        estado.textContent = t.no_se_pudo + e.message;
        estado.className = "mensaje error";
      }
      estado.hidden = false;
    });
    return;
  }

  // --- Prepara el enlace para llevárselo --------------------------------------------------------
  const datos = { v: 1, p: mios.p, f: mios.f, r: repostajes().map(compactar) };
  const que = resumen(datos);
  if (!que) {
    $("pasar-lleva").textContent = t.nada;
    for (const id of ["pasar-qr", "pasar-copiar"]) $(id).hidden = true;
    return;
  }
  $("pasar-lleva").textContent = t.lleva.replace("{que}", que);
  const enlace = `${base}pasar#${a64(JSON.stringify(datos))}`;
  if (enlace.length <= MAX_QR) {
    const qr = qrcode(0, "L");
    qr.addData(enlace);
    qr.make();
    $("pasar-qr").innerHTML = qr.createSvgTag({ cellSize: 4, margin: 2, scalable: true });
  } else {
    $("pasar-qr").hidden = true;
    $("pasar-grande").hidden = false;
  }
  if (navigator.share) {
    $("pasar-compartir").hidden = false;
    $("pasar-compartir").addEventListener("click", () => navigator.share({ title: "Pumpcast", url: enlace }).catch(() => {}));
  }
  $("pasar-copiar").addEventListener("click", async () => {
    await navigator.clipboard.writeText(enlace);
    $("pasar-copiar").textContent = t.copiado;
  });
})();

// La bienvenida: un paso cada vez. Con la ubicación puesta pasa al combustible, y al elegirlo, al radio.
(() => {
  const $ = (id) => document.getElementById(id);
  const { paso: textoPaso, lista: textoLista } = window.BIENVENIDA;
  const { t, lang } = window.I18N;
  const pasos = [...document.querySelectorAll("#bienvenida .paso")];
  const estado = $("bien-estado");
  const atras = $("bien-atras");
  let actual = 1;

  function ir(n, enfocar = true) {
    actual = n;
    for (const p of pasos) p.hidden = Number(p.dataset.paso) !== n;
    $("bien-paso").hidden = false;
    $("bien-paso").textContent = textoPaso.replace("{n}", n);
    atras.hidden = n === 1;
    if (enfocar) pasos[n - 1].querySelector("input:checked, button, input")?.focus({ preventScroll: true });
  }
  atras.addEventListener("click", () => ir(actual - 1));

  function poner(lat, lon) {
    $("bien-lat").value = lat.toFixed(5);
    $("bien-lon").value = lon.toFixed(5);
    $("bien-resultados").replaceChildren();
    estado.textContent = textoLista;
    setTimeout(() => ir(2), 450);                  // que se vea el «lista» antes de pasar
  }

  $("bien-gps").addEventListener("click", () => {
    if (!navigator.geolocation) { estado.textContent = t.sin_gps; return; }
    estado.textContent = t.buscando_gps;
    navigator.geolocation.getCurrentPosition(
      (pos) => poner(pos.coords.latitude, pos.coords.longitude),
      (err) => { estado.textContent = t.no_se_pudo + err.message; },
      { enableHighAccuracy: true, timeout: 15000 });
  });

  async function buscar() {
    const q = $("bien-buscar").value.trim();
    const lista = $("bien-resultados");
    lista.replaceChildren();
    if (q.length < 3) { estado.textContent = t.escribe_mas; return; }
    estado.textContent = t.buscando;
    try {
      const r = await fetch("https://nominatim.openstreetmap.org/search?" + new URLSearchParams(
        { q, format: "jsonv2", limit: "5", countrycodes: "es", "accept-language": lang }));
      if (!r.ok) throw new Error(r.status);
      const resultados = await r.json();
      if (!resultados.length) { estado.textContent = t.no_encontrada; return; }
      estado.textContent = t.elige + " " + t.fuente_busqueda;
      for (const d of resultados) {
        const li = document.createElement("li");
        const boton = document.createElement("button");
        boton.type = "button";
        boton.textContent = d.display_name;
        boton.addEventListener("click", () => poner(parseFloat(d.lat), parseFloat(d.lon)));
        li.append(boton);
        lista.append(li);
      }
    } catch (e) {
      estado.textContent = t.no_se_pudo_buscar + e.message;
    }
  }
  $("bien-buscar-boton").addEventListener("click", buscar);
  $("bien-buscar").addEventListener("keydown", (e) => { if (e.key === "Enter") { e.preventDefault(); buscar(); } });

  for (const radio of document.querySelectorAll('#bienvenida input[name="combustible"]')) {
    radio.addEventListener("click", () => setTimeout(() => ir(3), 250));   // «click»: también si ya estaba elegido
  }
  $("bienvenida").addEventListener("submit", (e) => {
    if (!$("bien-lat").value) { e.preventDefault(); ir(1); estado.textContent = t.falta_ubicacion; }
  });

  ir(1, false);
})();

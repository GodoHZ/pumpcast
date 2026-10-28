// Mis repostajes: se apuntan y se guardan solo en este navegador (localStorage). El servidor no
// los ve. Con dos repostajes de depósito lleno con los km del cuentakilómetros sale el consumo real.
(() => {
  const $ = (id) => document.getElementById(id);
  const T = window.REPOSTAJES;
  const { lang, europeo } = window.I18N;
  const CLAVE = "pumpcast_repostajes";
  const KM_MINIMOS = 100;                     // con menos, el consumo sale a voleo
  const local = europeo ? "es-ES" : "en-GB";
  const euros = new Intl.NumberFormat(local, { style: "currency", currency: "EUR" });
  const decimal = (n, d) => new Intl.NumberFormat(local, { minimumFractionDigits: d, maximumFractionDigits: d }).format(n);
  const fechaCorta = (iso) => new Date(iso + "T12:00").toLocaleDateString(lang, { day: "numeric", month: "short", year: "numeric" });
  const numero = (texto) => parseFloat(String(texto).trim().replace(/\s/g, "").replace(",", "."));

  function leer() {
    try {
      const lista = JSON.parse(localStorage.getItem(CLAVE) || "[]");
      return Array.isArray(lista) ? lista.filter(valido) : [];
    } catch (e) {
      return [];
    }
  }
  function escribir(lista) {
    try { localStorage.setItem(CLAVE, JSON.stringify(lista)); } catch (e) { /* modo privado: solo esta visita */ }
  }
  function valido(r) {
    return r && /^\d{4}-\d{2}-\d{2}$/.test(r.fecha) && r.litros > 0 && r.litros < 500 && r.precio > 0 && r.precio < 10
      && (r.km == null || (r.km >= 0 && r.km < 5e6));
  }
  const ordenados = (lista) => [...lista].sort((a, b) => a.fecha.localeCompare(b.fecha) || (a.km ?? 0) - (b.km ?? 0));

  // Litros por 100 km entre el primer y el último depósito lleno con km: todo lo echado después
  // del primero (hasta el último, incluido) es lo que se gastó en esos km.
  function consumo(lista) {
    const orden = ordenados(lista);
    const llenos = orden.map((r, i) => [r, i]).filter(([r]) => r.lleno && r.km != null);
    if (llenos.length < 2) return null;
    const [primero, i] = llenos[0];
    const [ultimo, j] = llenos[llenos.length - 1];
    const km = ultimo.km - primero.km;
    if (km < KM_MINIMOS) return null;
    const litros = orden.slice(i + 1, j + 1).reduce((s, r) => s + r.litros, 0);
    return (litros / km) * 100;
  }

  // La media de la zona del día del repostaje (o de los días de antes, por si ese no hubo lectura).
  const DIAS_HACIA_ATRAS = 3;
  function mediaDe(fecha) {
    const d = new Date(fecha + "T12:00");
    for (let i = 0; i <= DIAS_HACIA_ATRAS; i++) {
      const media = T.medias[new Date(d - i * 864e5).toISOString().slice(0, 10)];
      if (media) return media;
    }
    return null;
  }

  // Lo ahorrado en los últimos 12 meses: litros × (media de ese día − lo que pagaste).
  function pintarAhorro(lista, hace12) {
    const cuentan = lista.filter((r) => r.fecha > hace12 && mediaDe(r.fecha));
    const cifra = $("rep-ahorro-cifra");
    if (!cuentan.length) {
      cifra.hidden = $("rep-ahorro-nota").hidden = true;
      return;
    }
    const ahorro = cuentan.reduce((s, r) => s + r.litros * (mediaDe(r.fecha) - r.precio), 0);
    cifra.hidden = $("rep-ahorro-nota").hidden = false;
    cifra.textContent = euros.format(Math.abs(ahorro));
    cifra.classList.toggle("baja", ahorro >= 0);
    cifra.classList.toggle("sube", ahorro < 0);
    $("rep-ahorro-texto").textContent = ahorro >= 0 ? T.ahorro_bien : T.ahorro_mal;
    $("rep-ahorro-nota").textContent = T.ahorro_nota.replace("{n}", cuentan.length);
  }

  function pintar() {
    const lista = leer();
    const orden = ordenados(lista).reverse();
    $("rep-vacio").hidden = lista.length > 0;
    $("rep-cifras").hidden = lista.length === 0;
    const hoy = new Date().toISOString().slice(0, 10);
    const hace12 = new Date(Date.now() - 365 * 864e5).toISOString().slice(0, 10);
    const gasto = (filtro) => lista.filter(filtro).reduce((s, r) => s + r.litros * r.precio, 0);
    $("rep-mes").textContent = euros.format(gasto((r) => r.fecha.slice(0, 7) === hoy.slice(0, 7)));
    $("rep-anio").textContent = euros.format(gasto((r) => r.fecha > hace12));
    pintarAhorro(lista, hace12);
    const c = consumo(lista);
    $("rep-consumo").textContent = c ? decimal(c, 1) : "–";
    $("rep-consumo-nota").hidden = c !== null || lista.length === 0;
    const usar = $("rep-usar");
    usar.hidden = c === null;
    if (c !== null) {
      usar.href = "/ajustes?consumo=" + c.toFixed(1);
      usar.title = T.consumo_valor.replace("{consumo}", decimal(c, 1));
    }

    const ul = $("rep-lista");
    ul.replaceChildren();
    for (const r of orden) {
      const li = document.createElement("li");
      const fila = document.createElement("div");
      fila.className = "fila-rep";
      const total = document.createElement("span");
      total.className = "precio";
      total.textContent = euros.format(r.litros * r.precio);
      const info = document.createElement("span");
      info.className = "info";
      const titulo = document.createElement("b");
      titulo.textContent = `${fechaCorta(r.fecha)} · ${decimal(r.litros, 2)} ${T.unidad} × ${decimal(r.precio, 3)}`;
      const detalle = document.createElement("small");
      const media = mediaDe(r.fecha);
      const dif = media ? (r.precio - media) * 100 : null;
      const frente = dif === null ? "" : T.frente_media.replace("{dif}", (dif > 0 ? "+" : dif < 0 ? "−" : "") + decimal(Math.abs(dif), 1));
      detalle.textContent = [r.estacion, r.km != null ? T.km.replace("{km}", decimal(r.km, 0)) : "", r.lleno ? T.lleno : "", frente]
        .filter(Boolean).join(" · ");
      info.append(titulo, detalle);
      const borrar = document.createElement("button");
      borrar.type = "button";
      borrar.className = "boton-icono";
      borrar.textContent = "✕";
      borrar.setAttribute("aria-label", T.borrar);
      borrar.addEventListener("click", () => {
        if (!confirm(T.borrar_seguro)) return;
        escribir(leer().filter((x) => x.id !== r.id));
        pintar();
      });
      fila.append(total, info, borrar);
      li.append(fila);
      ul.append(li);
    }
  }

  const form = $("rep-form");
  form.fecha.value = new Date().toISOString().slice(0, 10);
  form.addEventListener("submit", (e) => {
    e.preventDefault();
    const km = form.km.value.trim() === "" ? null : Math.round(numero(form.km.value));
    const r = {
      id: Date.now().toString(36) + Math.random().toString(36).slice(2, 6),
      fecha: form.fecha.value, litros: numero(form.litros.value), precio: numero(form.precio.value),
      km: Number.isNaN(km) ? -1 : km, lleno: form.lleno.checked, estacion: form.estacion.value.slice(0, 80),
    };
    const error = $("rep-error");
    error.hidden = valido(r);
    if (!valido(r)) { error.textContent = T.error; return; }
    escribir([...leer(), r]);
    form.litros.value = "";
    form.km.value = "";
    pintar();
  });

  // Copia de seguridad: el navegador puede borrar lo guardado (limpiar datos, otro móvil...).
  $("rep-exportar").addEventListener("click", () => {
    const blob = new Blob([JSON.stringify(leer(), null, 1)], { type: "application/json" });
    const a = document.createElement("a");
    a.href = URL.createObjectURL(blob);
    a.download = `pumpcast-repostajes-${new Date().toISOString().slice(0, 10)}.json`;
    a.click();
    setTimeout(() => URL.revokeObjectURL(a.href), 1000);
  });
  $("rep-importar").addEventListener("change", async (e) => {
    const fichero = e.target.files[0];
    if (!fichero) return;
    try {
      const nuevos = JSON.parse(await fichero.text()).filter(valido);
      const ya = new Set(leer().map((r) => r.id));
      const sumar = nuevos.filter((r) => !ya.has(r.id)).map((r) => ({ ...r, id: String(r.id || Math.random()) }));
      escribir([...leer(), ...sumar]);
      pintar();
      alert(T.importados.replace("{n}", sumar.length));
    } catch (err) {
      alert(T.importar_mal);
    }
    e.target.value = "";
  });

  pintar();
})();

// Gráficas de líneas con los colores de la app. Necesita Chart.js cargado antes.
// `secundaria` (opcional) va en su propio eje a la derecha, p. ej. el Brent en €/barril.
function lineas(id, fechas, series, secundaria) {
  const css = getComputedStyle(document.documentElement);
  const color = (nombre) => css.getPropertyValue(nombre).trim();
  const marca = color("--tinta-marca") || color("--marca");
  const suave = color("--suave");
  const borde = color("--borde");
  const petroleo = color("--petroleo");
  const { europeo, decimal } = window.I18N;
  const etiquetas = fechas.map((f) => { const [, m, d] = f.split("-"); return europeo ? `${+d}/${+m}` : `${+m}/${+d}`; });
  const cifra = (v, d) => v.toFixed(d).replace(".", decimal);
  const moneda = (v, d) => v == null ? "–" : (europeo ? `${cifra(v, d)} €` : `€${cifra(v, d)}`);
  const euros = (v) => moneda(v, 3);

  const datasets = series.map((s) => ({
    label: s.label,
    data: s.data,
    yAxisID: "y",
    borderColor: s.principal ? marca : suave,
    borderWidth: s.principal ? 2.5 : 1.5,
    borderDash: s.principal ? [] : [5, 4],
    pointRadius: 0,
    pointHitRadius: 12,
    tension: 0.25,
    spanGaps: true,
  }));
  const conSecundaria = Boolean(secundaria && secundaria.data.some((v) => v != null));
  const ultimaSecundaria = conSecundaria ? secundaria.data.findLastIndex((v) => v != null) : -1;
  if (conSecundaria) {
    datasets.push({
      label: secundaria.label, data: secundaria.data, yAxisID: "y2", borderColor: petroleo,
      borderWidth: 1.5, pointRadius: 0, pointHitRadius: 12, tension: 0.25, spanGaps: true,
    });
  }

  new Chart(document.getElementById(id), {
    type: "line",
    data: { labels: etiquetas, datasets },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      animation: false,
      interaction: { mode: "index", intersect: false },
      plugins: {
        legend: { labels: { color: suave, boxWidth: 14, boxHeight: 2 } },
        tooltip: {
          callbacks: {
            // Los últimos días aún no tienen Brent (se publica con retraso): decirlo en vez de callarlo.
            footer: (items) => conSecundaria && items.length && items[0].dataIndex > ultimaSecundaria
              ? `${secundaria.label}: ${window.I18N.t.brent_pendiente}` : "",
            label: (c) => `${c.dataset.label}: ${c.dataset.yAxisID === "y2" ? moneda(c.parsed.y, 2) : euros(c.parsed.y)}`,
          },
        },
      },
      scales: {
        x: { ticks: { color: suave, maxTicksLimit: 6, maxRotation: 0 }, grid: { display: false } },
        y: { ticks: { color: suave, callback: (v) => cifra(v, 2) }, grid: { color: borde } },
        y2: {
          display: conSecundaria, position: "right", grid: { display: false },
          ticks: { color: petroleo, callback: (v) => Math.round(v) },
        },
      },
    },
  });
}

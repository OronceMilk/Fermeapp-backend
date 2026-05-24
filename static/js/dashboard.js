function hasChartData(values) {
  return Array.isArray(values) && values.some((value) => Number(value) > 0);
}

function renderEmptyCanvas(canvas, message) {
  const wrapper = canvas.parentElement;
  if (!wrapper) return;
  wrapper.innerHTML = `
    <div class="grid h-full place-items-center rounded-xl border border-dashed border-slate-300 bg-slate-50 text-center">
      <div>
        <p class="font-semibold text-slate-700">${message}</p>
        <p class="mt-1 text-sm text-slate-500">Les graphiques se rempliront avec les prochaines saisies.</p>
      </div>
    </div>
  `;
}

function initialiserGraphiques() {
  if (!window.Chart || !window.FERMEAPP_CHARTS) return;

  const production = window.FERMEAPP_CHARTS.production || {};
  const productionCanvas = document.getElementById('productionChart');
  if (productionCanvas) {
    if (!hasChartData(production.data)) {
      renderEmptyCanvas(productionCanvas, 'Aucune donnée de production');
    } else {
      new Chart(productionCanvas, {
        type: 'line',
        data: {
          labels: production.labels || [],
          datasets: [{
            label: 'Œufs collectés',
            data: production.data || [],
            borderColor: '#7CB518',
            backgroundColor: 'rgba(124, 181, 24, 0.12)',
            fill: true,
            tension: 0.35,
            borderWidth: 3,
            pointRadius: 3
          }]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          plugins: { legend: { display: false } },
          scales: {
            y: { beginAtZero: true, grid: { color: '#EEF2F7' } },
            x: { grid: { display: false } }
          }
        }
      });
    }
  }

  const species = window.FERMEAPP_CHARTS.species || {};
  const speciesCanvas = document.getElementById('speciesChart');
  if (speciesCanvas) {
    if (!hasChartData(species.data)) {
      renderEmptyCanvas(speciesCanvas, 'Aucun animal enregistré');
    } else {
      new Chart(speciesCanvas, {
        type: 'doughnut',
        data: {
          labels: species.labels || [],
          datasets: [{
            data: species.data || [],
            backgroundColor: ['#7CB518', '#1A3A5C', '#2E6DA4', '#F59E0B', '#EF4444', '#64748B'],
            borderWidth: 0
          }]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          plugins: {
            legend: { position: 'bottom', labels: { usePointStyle: true, padding: 18 } }
          },
          cutout: '68%'
        }
      });
    }
  }
}

document.addEventListener('DOMContentLoaded', initialiserGraphiques);

document.addEventListener('DOMContentLoaded', () => {
    const ctxFinances = document.getElementById('financesChart');
    
    if (ctxFinances) {
        new Chart(ctxFinances, {
            type: 'bar',
            data: {
                labels: ['Jan', 'Fév', 'Mar', 'Avr', 'Mai', 'Juin', 'Juil', 'Août', 'Sep', 'Oct', 'Nov', 'Déc'],
                datasets: [
                    {
                        label: 'Recettes (Ventes œufs, animaux)',
                        data: [1200000, 1350000, 1100000, 1450000, 0, 0, 0, 0, 0, 0, 0, 0], // Le backend injectera ces données
                        backgroundColor: '#7cb518',
                        borderRadius: 4,
                    },
                    {
                        label: 'Dépenses (Aliments, Soins, Salaires)',
                        data: [800000, 950000, 750000, 820000, 0, 0, 0, 0, 0, 0, 0, 0], // Le backend injectera ces données
                        backgroundColor: '#ef4444', // Rouge
                        borderRadius: 4,
                    }
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'top',
                        labels: { usePointStyle: true, boxWidth: 8 }
                    },
                    tooltip: {
                        callbacks: {
                            label: function(context) {
                                let label = context.dataset.label || '';
                                if (label) { label += ': '; }
                                if (context.parsed.y !== null) {
                                    // Formate avec des espaces pour les milliers (ex: 1 450 000 FCFA)
                                    label += new Intl.NumberFormat('fr-FR').format(context.parsed.y) + ' FCFA';
                                }
                                return label;
                            }
                        }
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        grid: { borderDash: [2, 4], color: '#f3f4f6' },
                        ticks: {
                            callback: function(value) {
                                // Raccourci pour l'axe Y (ex: 1M, 500k)
                                if (value >= 1000000) return (value / 1000000) + 'M';
                                if (value >= 1000) return (value / 1000) + 'k';
                                return value;
                            }
                        }
                    },
                    x: {
                        grid: { display: false }
                    }
                }
            }
        });
    }
});
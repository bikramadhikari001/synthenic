let charts = new Map();

function initializeCharts() {
    // First destroy all existing charts
    charts.forEach(chart => {
        chart.destroy();
    });
    charts.clear();

    // Create new charts
    document.querySelectorAll('canvas[id^="dist-"]').forEach(function(canvas) {
        const histogram = JSON.parse(canvas.dataset.histogram);
        const bins = JSON.parse(canvas.dataset.bins);
        const labels = [];
        for (let i = 0; i < bins.length - 1; i++) {
            labels.push(bins[i].toFixed(1) + ' - ' + bins[i + 1].toFixed(1));
        }

        const chart = new Chart(canvas.getContext('2d'), {
            type: 'bar',
            data: {
                labels: labels,
                datasets: [{
                    label: 'Frequency',
                    data: histogram,
                    backgroundColor: 'rgba(76, 175, 80, 0.5)',
                    borderColor: 'rgba(76, 175, 80, 1)',
                    borderWidth: 1
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: true,
                aspectRatio: 2,  // Width:Height ratio of 2:1
                plugins: {
                    legend: {
                        display: false
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true
                    }
                }
            }
        });

        charts.set(canvas.id, chart);
    });
}

// Initialize charts when DOM is loaded
document.addEventListener('DOMContentLoaded', initializeCharts);

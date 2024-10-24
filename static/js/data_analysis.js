document.addEventListener('DOMContentLoaded', function() {
    const columnList = document.querySelector('.column-list');
    const removeColumnsBtn = document.getElementById('remove-columns');
    const generateForm = document.getElementById('generate-form');
    const downloadReportBtn = document.getElementById('download-report');
    const toggleAdvancedBtn = document.getElementById('toggle-advanced');
    const advancedSettings = document.getElementById('advanced-settings');

    // Show/hide column details
    columnList.addEventListener('click', function(e) {
        if (e.target.classList.contains('btn-show-more')) {
            const column = e.target.dataset.column;
            const details = document.getElementById(`details-${column}`);
            if (details.style.display === 'none') {
                fetchColumnDetails(column).then(data => {
                    details.innerHTML = formatColumnDetails(data);
                    details.style.display = 'block';
                    e.target.textContent = 'Hide Details';
                });
            } else {
                details.style.display = 'none';
                e.target.textContent = 'Show More';
            }
        }
    });

    // Remove selected columns
    removeColumnsBtn.addEventListener('click', function() {
        const selectedColumns = Array.from(document.querySelectorAll('input[name="columns"]:checked')).map(input => input.value);
        updateDataPreview(selectedColumns);
    });

    // Generate synthetic data
    generateForm.addEventListener('submit', function(e) {
        e.preventDefault();
        const formData = new FormData(generateForm);
        const progressBar = document.getElementById('progress-bar');
        progressBar.style.display = 'block';

        fetch(generateForm.action, {
            method: 'POST',
            body: formData
        })
        .then(response => response.json())
        .then(data => {
            progressBar.style.display = 'none';
            if (data.success) {
                alert('Synthetic data generated successfully!');
                window.location.href = data.redirect;
            } else {
                alert('Error generating synthetic data: ' + data.error);
            }
        })
        .catch(error => {
            progressBar.style.display = 'none';
            alert('An error occurred while generating synthetic data.');
            console.error('Error:', error);
        });
    });

    // Toggle advanced settings
    toggleAdvancedBtn.addEventListener('click', function() {
        advancedSettings.style.display = advancedSettings.style.display === 'none' ? 'block' : 'none';
    });

    // Download analysis report
    downloadReportBtn.addEventListener('click', function() {
        fetch('/download-report', {
            method: 'GET'
        })
        .then(response => response.blob())
        .then(blob => {
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.style.display = 'none';
            a.href = url;
            a.download = 'data_analysis_report.pdf';
            document.body.appendChild(a);
            a.click();
            window.URL.revokeObjectURL(url);
        })
        .catch(error => console.error('Error:', error));
    });

    // Fetch column details from the server
    function fetchColumnDetails(column) {
        return fetch(`/column-details/${column}`)
            .then(response => response.json());
    }

    // Format column details for display
    function formatColumnDetails(data) {
        let html = `<p><strong>Data Type:</strong> ${data.dataType}</p>`;
        html += `<p><strong>Unique Values:</strong> ${data.uniqueValues}</p>`;
        html += `<p><strong>Missing Values:</strong> ${data.missingValues}</p>`;

        if (data.dataType === 'numeric') {
            html += `<p><strong>Min:</strong> ${data.min}</p>`;
            html += `<p><strong>Max:</strong> ${data.max}</p>`;
            html += `<p><strong>Mean:</strong> ${data.mean}</p>`;
            html += `<p><strong>Standard Deviation:</strong> ${data.std}</p>`;
            html += `<canvas id="chart-${data.column}"></canvas>`;
            setTimeout(() => createHistogram(data.column, data.histogram), 0);
        } else if (data.dataType === 'categorical') {
            html += `<p><strong>Top Categories:</strong></p>`;
            html += `<ul>`;
            data.topCategories.forEach(cat => {
                html += `<li>${cat.category}: ${cat.count}</li>`;
            });
            html += `</ul>`;
            html += `<canvas id="chart-${data.column}"></canvas>`;
            setTimeout(() => createBarChart(data.column, data.topCategories), 0);
        }

        return html;
    }

    // Create histogram for numeric data
    function createHistogram(column, data) {
        const ctx = document.getElementById(`chart-${column}`).getContext('2d');
        new Chart(ctx, {
            type: 'bar',
            data: {
                labels: data.bins,
                datasets: [{
                    label: 'Frequency',
                    data: data.frequencies,
                    backgroundColor: 'rgba(75, 192, 192, 0.6)'
                }]
            },
            options: {
                responsive: true,
                scales: {
                    y: {
                        beginAtZero: true
                    }
                }
            }
        });
    }

    // Create bar chart for categorical data
    function createBarChart(column, data) {
        const ctx = document.getElementById(`chart-${column}`).getContext('2d');
        new Chart(ctx, {
            type: 'bar',
            data: {
                labels: data.map(item => item.category),
                datasets: [{
                    label: 'Count',
                    data: data.map(item => item.count),
                    backgroundColor: 'rgba(75, 192, 192, 0.6)'
                }]
            },
            options: {
                responsive: true,
                scales: {
                    y: {
                        beginAtZero: true
                    }
                }
            }
        });
    }

    // Update data preview based on selected columns
    function updateDataPreview(selectedColumns) {
        const table = document.querySelector('#sample-data table');
        const headers = table.querySelectorAll('th');
        const rows = table.querySelectorAll('tbody tr');

        headers.forEach(header => {
            if (!selectedColumns.includes(header.textContent)) {
                header.style.display = 'none';
            } else {
                header.style.display = '';
            }
        });

        rows.forEach(row => {
            const cells = row.querySelectorAll('td');
            cells.forEach((cell, index) => {
                if (!selectedColumns.includes(headers[index].textContent)) {
                    cell.style.display = 'none';
                } else {
                    cell.style.display = '';
                }
            });
        });

        updateInsights(selectedColumns);
    }

    // Update insights based on selected columns
    function updateInsights(selectedColumns) {
        fetch('/update-insights', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ columns: selectedColumns }),
        })
        .then(response => response.json())
        .then(data => {
            const insightsContent = document.getElementById('insights-content');
            insightsContent.innerHTML = data.insights.map(insight => `<p>${insight}</p>`).join('');
        })
        .catch(error => console.error('Error:', error));
    }

    // Initial insights update
    updateInsights(Array.from(document.querySelectorAll('input[name="columns"]:checked')).map(input => input.value));
});

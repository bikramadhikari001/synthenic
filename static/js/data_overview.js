document.addEventListener('DOMContentLoaded', function() {
    // Tab Switching
    const tabBtns = document.querySelectorAll('.tab-btn');
    const tabContents = document.querySelectorAll('.tab-content');

    tabBtns.forEach(btn => {
        btn.addEventListener('click', () => {
            const tabId = btn.dataset.tab;
            
            // Update active states
            tabBtns.forEach(b => b.classList.remove('active'));
            tabContents.forEach(c => c.classList.remove('active'));
            
            btn.classList.add('active');
            document.getElementById(tabId).classList.add('active');

            // Initialize charts if switching to distributions tab
            if (tabId === 'distributions') {
                initializeCharts();
            }
        });
    });

    // Initialize Charts
    function initializeCharts() {
        const numericColumns = Array.from(document.querySelectorAll('.column-card'))
            .filter(card => {
                const typeText = card.querySelector('.stat-value').textContent;
                return ['int64', 'float64'].includes(typeText);
            })
            .map(card => ({
                name: card.querySelector('label').textContent,
                min: parseFloat(card.querySelector('.stat-row:last-child .stat-value').textContent.split('-')[0]),
                max: parseFloat(card.querySelector('.stat-row:last-child .stat-value').textContent.split('-')[1])
            }));

        numericColumns.forEach(column => {
            const ctx = document.getElementById(`dist-${column.name}`).getContext('2d');
            new Chart(ctx, {
                type: 'bar',
                data: {
                    labels: generateDistributionLabels(column.min, column.max, 10),
                    datasets: [{
                        label: `Distribution of ${column.name}`,
                        data: generateRandomDistribution(10),
                        backgroundColor: 'rgba(76, 175, 80, 0.5)',
                        borderColor: 'rgba(76, 175, 80, 1)',
                        borderWidth: 1
                    }]
                },
                options: {
                    responsive: true,
                    plugins: {
                        legend: {
                            display: false
                        },
                        title: {
                            display: true,
                            text: column.name
                        }
                    },
                    scales: {
                        y: {
                            beginAtZero: true
                        }
                    }
                }
            });
        });
    }

    function generateDistributionLabels(min, max, count) {
        const step = (max - min) / count;
        return Array.from({length: count}, (_, i) => 
            `${(min + i * step).toFixed(1)}-${(min + (i + 1) * step).toFixed(1)}`
        );
    }

    function generateRandomDistribution(count) {
        return Array.from({length: count}, () => Math.random() * 100);
    }

    // Model Selection
    const modelCards = document.querySelectorAll('.model-card');
    const modelRadios = document.querySelectorAll('input[name="model"]');

    modelCards.forEach(card => {
        card.addEventListener('click', () => {
            const radio = card.querySelector('input[type="radio"]');
            radio.checked = true;
            updateModelSelection(radio.value);
        });
    });

    modelRadios.forEach(radio => {
        radio.addEventListener('change', () => {
            updateModelSelection(radio.value);
        });
    });

    function updateModelSelection(modelName) {
        document.getElementById('selected-model').value = modelName;
        
        // Update UI to show active model
        modelCards.forEach(card => {
            if (card.dataset.model === modelName) {
                card.style.borderColor = '#4CAF50';
            } else {
                card.style.borderColor = '#e9ecef';
            }
        });
    }

    // Sample Size Presets
    const presetBtns = document.querySelectorAll('.preset-btn');
    const samplesInput = document.getElementById('samples');

    presetBtns.forEach(btn => {
        btn.addEventListener('click', () => {
            samplesInput.value = btn.dataset.value;
        });
    });

    // Column Selection
    const columnCheckboxes = document.querySelectorAll('input[name="columns"]');
    
    function updateSelectedColumns() {
        const selectedColumns = Array.from(columnCheckboxes)
            .filter(cb => cb.checked)
            .map(cb => cb.value);
        document.getElementById('selected-columns').value = JSON.stringify(selectedColumns);
    }

    columnCheckboxes.forEach(cb => {
        cb.addEventListener('change', updateSelectedColumns);
    });

    // Preview Modal
    const modal = document.getElementById('preview-modal');
    const closeBtn = document.querySelector('.close');

    window.previewSettings = function() {
        const modelName = document.querySelector('input[name="model"]:checked').value;
        const selectedColumns = JSON.parse(document.getElementById('selected-columns').value);
        const samples = document.getElementById('samples').value;
        const projectName = document.getElementById('project-name').value;

        // Get model-specific parameters
        const modelParams = {};
        const activeModel = document.querySelector('.model-card[data-model="' + modelName + '"]');
        activeModel.querySelectorAll('input[type="number"]').forEach(input => {
            modelParams[input.id] = input.value;
        });

        const previewHTML = `
            <div class="preview-section">
                <h3>Project Settings</h3>
                <p><strong>Project Name:</strong> ${projectName || 'Not set'}</p>
                <p><strong>Number of Samples:</strong> ${samples}</p>
                <p><strong>Selected Model:</strong> ${modelName}</p>
            </div>
            <div class="preview-section">
                <h3>Selected Columns</h3>
                <ul>
                    ${selectedColumns.map(col => `<li>${col}</li>`).join('')}
                </ul>
            </div>
            <div class="preview-section">
                <h3>Model Parameters</h3>
                <ul>
                    ${Object.entries(modelParams).map(([key, value]) => 
                        `<li><strong>${key}:</strong> ${value}</li>`
                    ).join('')}
                </ul>
            </div>
        `;

        document.getElementById('preview-content').innerHTML = previewHTML;
        modal.style.display = 'block';
    };

    closeBtn.addEventListener('click', () => {
        modal.style.display = 'none';
    });

    window.addEventListener('click', (e) => {
        if (e.target === modal) {
            modal.style.display = 'none';
        }
    });

    // Form Submission
    const generateForm = document.getElementById('generate-form');
    generateForm.addEventListener('submit', (e) => {
        e.preventDefault();
        
        // Collect model parameters
        const modelName = document.querySelector('input[name="model"]:checked').value;
        const modelParams = {};
        const activeModel = document.querySelector('.model-card[data-model="' + modelName + '"]');
        activeModel.querySelectorAll('input[type="number"]').forEach(input => {
            modelParams[input.id] = input.value;
        });

        document.getElementById('model-params').value = JSON.stringify(modelParams);
        
        // Update selected columns one last time
        updateSelectedColumns();
        
        // Submit the form
        generateForm.submit();
    });

    // Initialize
    updateSelectedColumns();
    updateModelSelection(document.querySelector('input[name="model"]:checked').value);
});

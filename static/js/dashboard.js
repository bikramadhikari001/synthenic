document.addEventListener('DOMContentLoaded', function() {
    console.log('Dashboard JS loaded');

    // Handle file upload
    const dropZone = document.querySelector('.upload-zone');
    const fileInput = document.createElement('input');
    fileInput.type = 'file';
    fileInput.accept = '.csv';
    fileInput.style.display = 'none';
    document.body.appendChild(fileInput);

    // Handle drag and drop
    dropZone.addEventListener('dragover', (e) => {
        e.preventDefault();
        dropZone.classList.add('dragover');
    });

    dropZone.addEventListener('dragleave', () => {
        dropZone.classList.remove('dragover');
    });

    dropZone.addEventListener('drop', (e) => {
        e.preventDefault();
        dropZone.classList.remove('dragover');
        const file = e.dataTransfer.files[0];
        if (file && file.name.endsWith('.csv')) {
            uploadFile(file);
        }
    });

    // Handle click to upload
    dropZone.addEventListener('click', () => {
        fileInput.click();
    });

    fileInput.addEventListener('change', (e) => {
        const file = e.target.files[0];
        if (file && file.name.endsWith('.csv')) {
            uploadFile(file);
        }
    });

    // Upload file function
    function uploadFile(file) {
        const formData = new FormData();
        formData.append('file', file);

        fetch('/data/upload-csv', {
            method: 'POST',
            body: formData
        })
        .then(response => {
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            window.location.href = response.url;
        })
        .catch(error => {
            console.error('Error:', error);
            alert('Error uploading file');
        });
    }

    // Handle project deletion
    document.querySelectorAll('.delete-btn').forEach(button => {
        button.addEventListener('click', function(e) {
            e.preventDefault();
            if (confirm('Are you sure you want to delete this project?')) {
                const projectId = this.getAttribute('data-project-id');
                fetch(`/data/delete-project/${projectId}`, {
                    method: 'POST'
                })
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        window.location.reload();
                    } else {
                        alert('Error deleting project');
                    }
                })
                .catch(error => {
                    console.error('Error:', error);
                    alert('Error deleting project');
                });
            }
        });
    });

    // Handle search
    const searchInput = document.querySelector('input[type="search"]');
    if (searchInput) {
        searchInput.addEventListener('input', function(e) {
            const searchTerm = e.target.value.toLowerCase();
            document.querySelectorAll('.project-card').forEach(card => {
                const projectName = card.querySelector('.project-name').textContent.toLowerCase();
                if (projectName.includes(searchTerm)) {
                    card.style.display = '';
                } else {
                    card.style.display = 'none';
                }
            });
        });
    }

    // Handle model filter
    const modelSelect = document.querySelector('.model-select');
    if (modelSelect) {
        modelSelect.addEventListener('change', function(e) {
            const selectedModel = e.target.value.toLowerCase();
            document.querySelectorAll('.project-card').forEach(card => {
                const projectModel = card.querySelector('.project-model').textContent.toLowerCase();
                if (selectedModel === 'all models' || projectModel === selectedModel) {
                    card.style.display = '';
                } else {
                    card.style.display = 'none';
                }
            });
        });
    }

    // Handle upload button
    const uploadBtn = document.querySelector('.upload-btn');
    if (uploadBtn) {
        uploadBtn.addEventListener('click', function(e) {
            e.preventDefault();
            fileInput.click();
        });
    }
});

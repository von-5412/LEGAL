// TOS Analyzer JavaScript
document.addEventListener('DOMContentLoaded', function() {
    const uploadZone = document.getElementById('upload-zone');
    const fileInput = document.getElementById('file-input');
    const analyzeBtn = document.getElementById('analyze-btn');
    const personaSelection = document.getElementById('persona-selection');

    // Click to upload
    uploadZone.addEventListener('click', () => {
        fileInput.click();
    });

    // Drag and drop handlers
    uploadZone.addEventListener('dragover', (e) => {
        e.preventDefault();
        uploadZone.classList.add('drag-over');
    });

    uploadZone.addEventListener('dragleave', () => {
        uploadZone.classList.remove('drag-over');
    });

    uploadZone.addEventListener('drop', (e) => {
        e.preventDefault();
        uploadZone.classList.remove('drag-over');
        
        const files = e.dataTransfer.files;
        if (files.length > 0) {
            fileInput.files = files;
            handleFileSelect();
        }
    });

    // File input change handler
    fileInput.addEventListener('change', handleFileSelect);

    function handleFileSelect() {
        const file = fileInput.files[0];
        if (file) {
            // Update upload zone to show selected file
            const uploadContent = uploadZone.querySelector('.upload-content');
            uploadContent.innerHTML = `
                <i class="fas fa-file-alt upload-icon"></i>
                <h4>${file.name}</h4>
                <p class="text-muted">File selected (${(file.size / 1024 / 1024).toFixed(2)} MB)</p>
            `;
            
            // Show analyze button and persona selection
            analyzeBtn.style.display = 'block';
            if (personaSelection) {
                personaSelection.style.display = 'block';
            }
        }
    }

    // Form submission handler
    const uploadForm = document.getElementById('upload-form');
    if (uploadForm) {
        uploadForm.addEventListener('submit', function(e) {
            // Show loading state
            analyzeBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Analyzing...';
            analyzeBtn.disabled = true;
        });
    }
});

// Chart.js initialization for results page
if (typeof Chart !== 'undefined') {
    document.addEventListener('DOMContentLoaded', function() {
        // Risk breakdown chart
        const breakdownChart = document.getElementById('breakdown-chart');
        if (breakdownChart) {
            const risksData = JSON.parse(breakdownChart.dataset.risks || '{}');
            
            const labels = Object.keys(risksData).map(key => 
                key.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())
            );
            const data = Object.values(risksData).map(risk => risk.count || 0);
            const colors = [
                '#dc3545', '#fd7e14', '#ffc107', '#20c997', 
                '#0dcaf0', '#6f42c1', '#e83e8c', '#6c757d'
            ];

            new Chart(breakdownChart, {
                type: 'doughnut',
                data: {
                    labels: labels,
                    datasets: [{
                        data: data,
                        backgroundColor: colors,
                        borderWidth: 2,
                        borderColor: '#fff'
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: {
                            position: 'bottom'
                        }
                    }
                }
            });
        }
    });
}
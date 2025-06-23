// TOS Analyzer JavaScript

class TOSAnalyzer {
    constructor() {
        this.initializeEventListeners();
        this.initializeCharts();
    }

    initializeEventListeners() {
        // File upload handling
        const fileInput = document.getElementById('file-input');
        const uploadZone = document.getElementById('upload-zone');
        const uploadForm = document.getElementById('upload-form');

        if (fileInput && uploadZone) {
            // Drag and drop functionality
            uploadZone.addEventListener('dragover', (e) => {
                e.preventDefault();
                uploadZone.classList.add('dragover');
            });

            uploadZone.addEventListener('dragleave', (e) => {
                e.preventDefault();
                uploadZone.classList.remove('dragover');
            });

            uploadZone.addEventListener('drop', (e) => {
                e.preventDefault();
                uploadZone.classList.remove('dragover');
                
                const files = e.dataTransfer.files;
                if (files.length > 0) {
                    fileInput.files = files;
                    this.handleFileSelect(files[0]);
                }
            });

            // Click to upload
            uploadZone.addEventListener('click', () => {
                fileInput.click();
            });

            fileInput.addEventListener('change', (e) => {
                if (e.target.files.length > 0) {
                    this.handleFileSelect(e.target.files[0]);
                }
            });
        }

        // Form submission
        if (uploadForm) {
            uploadForm.addEventListener('submit', (e) => {
                this.handleFormSubmit(e);
            });
        }

        // Flagged section toggles
        document.querySelectorAll('.flagged-section-toggle').forEach(toggle => {
            toggle.addEventListener('click', (e) => {
                e.preventDefault();
                const section = toggle.closest('.flagged-section');
                const content = section.querySelector('.flagged-section-content');
                
                if (content.style.display === 'none') {
                    content.style.display = 'block';
                    toggle.textContent = 'Hide Details';
                } else {
                    content.style.display = 'none';
                    toggle.textContent = 'Show Details';
                }
            });
        });
    }

    handleFileSelect(file) {
        const maxSize = 16 * 1024 * 1024; // 16MB
        const allowedTypes = ['text/plain', 'application/pdf'];

        if (file.size > maxSize) {
            this.showAlert('File too large. Maximum size is 16MB.', 'error');
            return;
        }

        if (!allowedTypes.includes(file.type) && !file.name.toLowerCase().endsWith('.txt') && !file.name.toLowerCase().endsWith('.pdf')) {
            this.showAlert('Invalid file type. Please upload a PDF or text file.', 'error');
            return;
        }

        // Update upload zone to show selected file
        const uploadZone = document.getElementById('upload-zone');
        const uploadText = uploadZone.querySelector('.upload-text');
        
        if (uploadText) {
            uploadText.innerHTML = `
                <div class="selected-file">
                    <i class="fas fa-file-alt upload-icon"></i>
                    <h3>Selected: ${file.name}</h3>
                    <p>Size: ${this.formatFileSize(file.size)} | Type: ${file.type}</p>
                    <button type="submit" class="btn btn-primary mt-2">
                        <i class="fas fa-search"></i> Analyze Document
                    </button>
                </div>
            `;
        }
    }

    handleFormSubmit(e) {
        const submitBtn = e.target.querySelector('button[type="submit"]');
        const fileInput = e.target.querySelector('input[type="file"]');

        if (!fileInput.files.length) {
            e.preventDefault();
            this.showAlert('Please select a file to analyze.', 'error');
            return;
        }

        // Show loading state
        if (submitBtn) {
            const originalText = submitBtn.innerHTML;
            submitBtn.innerHTML = '<span class="loading"></span> Analyzing...';
            submitBtn.disabled = true;

            // Re-enable button after 30 seconds as fallback
            setTimeout(() => {
                submitBtn.innerHTML = originalText;
                submitBtn.disabled = false;
            }, 30000);
        }
    }

    initializeCharts() {
        // Risk Score Chart
        const riskChartCanvas = document.getElementById('risk-chart');
        if (riskChartCanvas) {
            const ctx = riskChartCanvas.getContext('2d');
            const riskScore = parseInt(riskChartCanvas.dataset.score) || 0;
            
            new Chart(ctx, {
                type: 'doughnut',
                data: {
                    datasets: [{
                        data: [riskScore, 100 - riskScore],
                        backgroundColor: [
                            this.getRiskColor(riskScore),
                            '#E5E7EB'
                        ],
                        borderWidth: 0
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    cutout: '70%',
                    plugins: {
                        legend: {
                            display: false
                        },
                        tooltip: {
                            enabled: false
                        }
                    }
                }
            });
        }

        // Risk Breakdown Chart
        const breakdownChartCanvas = document.getElementById('breakdown-chart');
        if (breakdownChartCanvas) {
            const ctx = breakdownChartCanvas.getContext('2d');
            const riskData = JSON.parse(breakdownChartCanvas.dataset.risks || '{}');
            
            const labels = Object.keys(riskData).map(key => 
                key.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())
            );
            const data = Object.values(riskData).map(item => item.count * item.weight);
            
            new Chart(ctx, {
                type: 'bar',
                data: {
                    labels: labels,
                    datasets: [{
                        label: 'Risk Score',
                        data: data,
                        backgroundColor: '#DC2626',
                        borderColor: '#B91C1C',
                        borderWidth: 1
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    scales: {
                        y: {
                            beginAtZero: true,
                            max: 30
                        }
                    },
                    plugins: {
                        legend: {
                            display: false
                        }
                    }
                }
            });
        }

        // Dark Patterns Chart
        const darkPatternsCanvas = document.getElementById('dark-patterns-chart');
        if (darkPatternsCanvas) {
            const ctx = darkPatternsCanvas.getContext('2d');
            const darkPatterns = JSON.parse(darkPatternsCanvas.dataset.patterns || '{}');
            
            const labels = Object.keys(darkPatterns).map(key => 
                key.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())
            );
            const data = Object.values(darkPatterns).map(item => item.count);
            
            new Chart(ctx, {
                type: 'doughnut',
                data: {
                    labels: labels,
                    datasets: [{
                        data: data,
                        backgroundColor: [
                            '#D97706',
                            '#F59E0B',
                            '#FBBF24',
                            '#FCD34D'
                        ],
                        borderWidth: 2,
                        borderColor: '#FFFFFF'
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
    }

    getRiskColor(score) {
        if (score < 30) return '#059669'; // green
        if (score < 70) return '#D97706'; // orange
        return '#DC2626'; // red
    }

    getRiskLevel(score) {
        if (score < 30) return 'low';
        if (score < 70) return 'medium';
        return 'high';
    }

    formatFileSize(bytes) {
        if (bytes === 0) return '0 Bytes';
        const k = 1024;
        const sizes = ['Bytes', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    }

    showAlert(message, type = 'info') {
        const alertContainer = document.getElementById('alert-container') || document.body;
        const alertDiv = document.createElement('div');
        alertDiv.className = `alert alert-${type === 'error' ? 'danger' : type} alert-dismissible`;
        alertDiv.innerHTML = `
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;
        
        alertContainer.insertBefore(alertDiv, alertContainer.firstChild);
        
        // Auto-dismiss after 5 seconds
        setTimeout(() => {
            alertDiv.remove();
        }, 5000);
    }

    // Initialize transparency score animation
    animateTransparencyScore() {
        const meter = document.querySelector('.transparency-fill');
        if (meter) {
            const score = parseInt(meter.dataset.score) || 0;
            setTimeout(() => {
                meter.style.width = `${score}%`;
            }, 500);
        }
    }

    // Initialize risk score animation
    animateRiskScore() {
        const circle = document.querySelector('.risk-score-circle');
        if (circle) {
            const score = parseInt(circle.dataset.score) || 0;
            circle.style.setProperty('--score', score);
            
            // Add pulsing animation for high risk
            if (score > 70) {
                circle.classList.add('pulse-high-risk');
            }
        }
    }
}

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    const analyzer = new TOSAnalyzer();
    
    // Run animations if on results page
    if (document.querySelector('.results-page')) {
        analyzer.animateTransparencyScore();
        analyzer.animateRiskScore();
    }
});

// Add CSS for animations
const style = document.createElement('style');
style.textContent = `
    @keyframes pulse-high-risk {
        0% { box-shadow: 0 0 0 0 rgba(220, 38, 38, 0.7); }
        70% { box-shadow: 0 0 0 10px rgba(220, 38, 38, 0); }
        100% { box-shadow: 0 0 0 0 rgba(220, 38, 38, 0); }
    }
    
    .pulse-high-risk {
        animation: pulse-high-risk 2s infinite;
    }
    
    .selected-file {
        text-align: center;
    }
    
    .selected-file .upload-icon {
        color: #059669;
    }
`;
document.head.appendChild(style);

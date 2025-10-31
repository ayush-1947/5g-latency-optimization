// Load dashboard data
fetch('dashboard_data.json')
    .then(response => response.json())
    .then(data => {
        // Initialize dashboard with data
        initializeDashboard(data);
    })
    .catch(error => {
        console.error('Error loading dashboard data:', error);
    });

// Initialize dashboard with data
function initializeDashboard(data) {
    try {
        // Update KPI values
        document.getElementById('overall-latency-improvement').textContent = data.overall_latency_improvement.toFixed(1);
        document.getElementById('resource-utilization-improvement').textContent = data.resource_utilization_improvement.toFixed(1);
        
        // Update slice latencies
        for (const [slice, latencies] of Object.entries(data.slice_latencies)) {
            const baseElement = document.getElementById(`${slice}-base-latency`);
            const optElement = document.getElementById(`${slice}-opt-latency`);
            const impElement = document.getElementById(`${slice}-improvement`);
            
            if (baseElement && optElement) {
                baseElement.textContent = latencies.base.toFixed(3);
                optElement.textContent = latencies.optimized.toFixed(3);
                
                // Calculate and display improvement percentage
                if (impElement && latencies.base > 0) {
                    const improvement = ((latencies.base - latencies.optimized) / latencies.base) * 100;
                    impElement.textContent = improvement.toFixed(1);
                    
                    // Add color based on improvement
                    if (improvement > 0) {
                        impElement.classList.add('text-success');
                    } else {
                        impElement.classList.add('text-danger');
                    }
                }
            }
        }
        
        // Insert any additional dynamic content as needed
        console.log("Dashboard initialized successfully with data:", data);
    } catch (error) {
        console.error("Error initializing dashboard:", error);
    }
}

// Image modal functionality
function openImageModal(title, imageSrc) {
    const modalTitle = document.getElementById('imageModalLabel');
    const modalImage = document.getElementById('modalImage');
    
    if (modalTitle && modalImage) {
        modalTitle.textContent = title;
        modalImage.src = imageSrc;
        
        const imageModal = new bootstrap.Modal(document.getElementById('imageModal'));
        imageModal.show();
    } else {
        console.error("Modal elements not found");
    }
}

// Print dashboard functionality
function printDashboard() {
    window.print();
}

// Export to PDF functionality
function exportToPDF() {
    alert('Exporting dashboard to PDF. This feature requires additional PDF generation libraries.');
    // In a real implementation, you would use a library like jsPDF or html2pdf
}
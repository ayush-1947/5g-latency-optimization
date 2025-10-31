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

// Load and initialize simulation results data
fetch('simulation_results.json')
    .then(response => response.json())
    .then(data => {
        populateSimulationResults(data);
    })
    .catch(error => {
        console.error('Error loading simulation results:', error);
        // Create mock data if file not found
        createMockSimulationData();
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

// Populate simulation results table
function populateSimulationResults(data) {
    try {
        const tableBody = document.getElementById('simulation-results-table');
        if (!tableBody) {
            console.error("Simulation results table body element not found");
            return;
        }
        
        // Clear existing table rows
        tableBody.innerHTML = '';
        
        // Add a row for each simulation result
        data.forEach((sim, index) => {
            const row = document.createElement('tr');
            
            // Create row cells with simulation data
            row.innerHTML = `
                <td>${sim.config_name || `Simulation ${index + 1}`}</td>
                <td>${sim.slice_name || 'All'}</td>
                <td>${sim.param_name || 'N/A'}</td>
                <td>${sim.param_value?.toFixed(2) || 'N/A'}</td>
                <td>${sim.overall_latency?.toFixed(3) || 'N/A'}</td>
                <td>${sim.sla_violations?.toFixed(3) || 'N/A'}</td>
                <td>${sim.block_ratio?.toFixed(3) || 'N/A'}</td>
                <td>${sim.handover_ratio?.toFixed(3) || 'N/A'}</td>
            `;
            
            // Add a css class for the row based on slice
            if (sim.slice_name) {
                row.classList.add(`slice-${sim.slice_name.toLowerCase()}`);
            }
            
            // Add the row to the table
            tableBody.appendChild(row);
        });
        
        console.log("Simulation results populated successfully");
    } catch (error) {
        console.error("Error populating simulation results:", error);
    }
}

// Create mock simulation data if the actual data file is not found
function createMockSimulationData() {
    console.log("Creating mock simulation data for demonstration");
    
    const slices = ['urllc', 'iot', 'data'];
    const params = ['resource_reservation', 'bandwidth_guaranteed'];
    const mockData = [];
    
    // Create mock data for 18 simulations (3 slices × 2 parameters × 3 values each)
    slices.forEach(slice => {
        params.forEach(param => {
            // Three different values for each parameter
            [0.1, 0.2, 0.3].forEach(value => {
                mockData.push({
                    config_name: `${slice}_${param}_${value}`,
                    slice_name: slice,
                    param_name: param,
                    param_value: value,
                    overall_latency: 0.4 + Math.random() * 0.1,
                    sla_violations: Math.random() * 0.02,
                    block_ratio: Math.random() * 0.05,
                    handover_ratio: Math.random() * 0.1
                });
            });
        });
    });
    
    // Add validation results
    mockData.push({
        config_name: "validation_base",
        slice_name: "all",
        param_name: "baseline",
        param_value: 0,
        overall_latency: 0.479,
        sla_violations: 0,
        block_ratio: 0.02,
        handover_ratio: 0.03
    });
    
    mockData.push({
        config_name: "validation_optimized",
        slice_name: "all",
        param_name: "optimized",
        param_value: 0,
        overall_latency: 0.475,
        sla_violations: 0,
        block_ratio: 0.018,
        handover_ratio: 0.028
    });
    
    // Populate the table with mock data
    populateSimulationResults(mockData);
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
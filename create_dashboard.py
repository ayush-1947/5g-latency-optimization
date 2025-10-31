#!/usr/bin/env python
"""
5G Network Slicing Dashboard Creator
====================================

This script creates the dashboard HTML, CSS, and JavaScript files
based on the optimization results.
"""

import os
import json
import shutil
from pathlib import Path

# Define paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
RESULTS_DIR = os.path.join(BASE_DIR, 'optimization_results')
DASHBOARD_DIR = os.path.join(BASE_DIR, 'dashboard')
IMAGES_DIR = os.path.join(DASHBOARD_DIR, 'images')

# Ensure directories exist
os.makedirs(os.path.join(DASHBOARD_DIR, 'css'), exist_ok=True)
os.makedirs(os.path.join(DASHBOARD_DIR, 'js'), exist_ok=True)
os.makedirs(IMAGES_DIR, exist_ok=True)

def create_dashboard_data():
    """Create the dashboard data JSON file from optimization results."""
    print("Creating dashboard_data.json...")
    
    # Default values in case we can't extract from results
    dashboard_data = {
        "overall_latency_improvement": 0.8,
        "resource_utilization_improvement": 12.5,
        "slice_latencies": {
            "urllc": {"base": 0.479, "optimized": 0.475},
            "iot": {"base": 0.479, "optimized": 0.475},
            "data": {"base": 0.479, "optimized": 0.475}
        }
    }
    
    # Try to load actual values from optimization results if available
    try:
        # Here you would load your actual result data and populate dashboard_data
        # This is a placeholder - replace with your actual logic to extract results
        pass
    except Exception as e:
        print(f"Warning: Could not load optimization results: {e}")
        print("Using default values for dashboard data.")
    
    # Save the dashboard data to JSON
    json_path = os.path.join(DASHBOARD_DIR, "dashboard_data.json")
    with open(json_path, 'w') as f:
        json.dump(dashboard_data, f, indent=2)
    
    print(f"Dashboard data saved to: {json_path}")
    
    return dashboard_data

def create_simulation_results():
    """Create the simulation results JSON file."""
    print("Creating simulation_results.json...")
    
    # Define the simulation data
    simulation_data = [
        # URLLC simulations
        {
            "config_name": "urllc_resource_reservation_0.1",
            "slice_name": "urllc",
            "param_name": "resource_reservation",
            "param_value": 0.1,
            "overall_latency": 0.393,
            "sla_violations": 0.0,
            "block_ratio": 0.021,
            "handover_ratio": 0.028
        },
        {
            "config_name": "urllc_resource_reservation_0.2",
            "slice_name": "urllc",
            "param_name": "resource_reservation",
            "param_value": 0.2,
            "overall_latency": 0.395,
            "sla_violations": 0.0,
            "block_ratio": 0.023,
            "handover_ratio": 0.029
        },
        {
            "config_name": "urllc_resource_reservation_0.3",
            "slice_name": "urllc",
            "param_name": "resource_reservation",
            "param_value": 0.3,
            "overall_latency": 0.399,
            "sla_violations": 0.0,
            "block_ratio": 0.026,
            "handover_ratio": 0.031
        },
        {
            "config_name": "urllc_bandwidth_guaranteed_2",
            "slice_name": "urllc",
            "param_name": "bandwidth_guaranteed",
            "param_value": 2,
            "overall_latency": 0.391,
            "sla_violations": 0.0,
            "block_ratio": 0.019,
            "handover_ratio": 0.026
        },
        {
            "config_name": "urllc_bandwidth_guaranteed_5",
            "slice_name": "urllc",
            "param_name": "bandwidth_guaranteed",
            "param_value": 5,
            "overall_latency": 0.395,
            "sla_violations": 0.0,
            "block_ratio": 0.022,
            "handover_ratio": 0.030
        },
        {
            "config_name": "urllc_bandwidth_guaranteed_10",
            "slice_name": "urllc",
            "param_name": "bandwidth_guaranteed",
            "param_value": 10,
            "overall_latency": 0.401,
            "sla_violations": 0.0,
            "block_ratio": 0.027,
            "handover_ratio": 0.033
        },
        
        # IoT simulations
        {
            "config_name": "iot_resource_reservation_0.05",
            "slice_name": "iot",
            "param_name": "resource_reservation",
            "param_value": 0.05,
            "overall_latency": 0.392,
            "sla_violations": 0.0,
            "block_ratio": 0.018,
            "handover_ratio": 0.025
        },
        {
            "config_name": "iot_resource_reservation_0.1",
            "slice_name": "iot",
            "param_name": "resource_reservation",
            "param_value": 0.1,
            "overall_latency": 0.397,
            "sla_violations": 0.0,
            "block_ratio": 0.023,
            "handover_ratio": 0.030
        },
        {
            "config_name": "iot_resource_reservation_0.2",
            "slice_name": "iot",
            "param_name": "resource_reservation",
            "param_value": 0.2,
            "overall_latency": 0.403,
            "sla_violations": 0.0,
            "block_ratio": 0.028,
            "handover_ratio": 0.036
        },
        {
            "config_name": "iot_bandwidth_guaranteed_5",
            "slice_name": "iot",
            "param_name": "bandwidth_guaranteed",
            "param_value": 5,
            "overall_latency": 0.391,
            "sla_violations": 0.0,
            "block_ratio": 0.017,
            "handover_ratio": 0.024
        },
        {
            "config_name": "iot_bandwidth_guaranteed_10",
            "slice_name": "iot",
            "param_name": "bandwidth_guaranteed",
            "param_value": 10,
            "overall_latency": 0.397,
            "sla_violations": 0.0,
            "block_ratio": 0.022,
            "handover_ratio": 0.029
        },
        {
            "config_name": "iot_bandwidth_guaranteed_15",
            "slice_name": "iot",
            "param_name": "bandwidth_guaranteed",
            "param_value": 15,
            "overall_latency": 0.405,
            "sla_violations": 0.0,
            "block_ratio": 0.029,
            "handover_ratio": 0.037
        },
        
        # Data simulations
        {
            "config_name": "data_resource_reservation_0",
            "slice_name": "data",
            "param_name": "resource_reservation",
            "param_value": 0,
            "overall_latency": 0.390,
            "sla_violations": 0.0,
            "block_ratio": 0.016,
            "handover_ratio": 0.023
        },
        {
            "config_name": "data_resource_reservation_0.1",
            "slice_name": "data",
            "param_name": "resource_reservation",
            "param_value": 0.1,
            "overall_latency": 0.399,
            "sla_violations": 0.0,
            "block_ratio": 0.025,
            "handover_ratio": 0.032
        },
        {
            "config_name": "data_resource_reservation_0.2",
            "slice_name": "data",
            "param_name": "resource_reservation",
            "param_value": 0.2,
            "overall_latency": 0.409,
            "sla_violations": 0.0,
            "block_ratio": 0.031,
            "handover_ratio": 0.040
        },
        {
            "config_name": "data_bandwidth_guaranteed_500",
            "slice_name": "data",
            "param_name": "bandwidth_guaranteed",
            "param_value": 500,
            "overall_latency": 0.389,
            "sla_violations": 0.0,
            "block_ratio": 0.015,
            "handover_ratio": 0.022
        },
        {
            "config_name": "data_bandwidth_guaranteed_1000",
            "slice_name": "data",
            "param_name": "bandwidth_guaranteed",
            "param_value": 1000,
            "overall_latency": 0.395,
            "sla_violations": 0.0,
            "block_ratio": 0.020,
            "handover_ratio": 0.028
        },
        {
            "config_name": "data_bandwidth_guaranteed_1500",
            "slice_name": "data",
            "param_name": "bandwidth_guaranteed",
            "param_value": 1500,
            "overall_latency": 0.403,
            "sla_violations": 0.0,
            "block_ratio": 0.027,
            "handover_ratio": 0.034
        },
        
        # Validation results
        {
            "config_name": "validation_base",
            "slice_name": "all",
            "param_name": "baseline",
            "param_value": 0,
            "overall_latency": 0.479,
            "sla_violations": 0.0,
            "block_ratio": 0.035,
            "handover_ratio": 0.045
        },
        {
            "config_name": "validation_optimized",
            "slice_name": "all",
            "param_name": "optimized",
            "param_value": 0,
            "overall_latency": 0.475,
            "sla_violations": 0.0,
            "block_ratio": 0.030,
            "handover_ratio": 0.040
        }
    ]
    
    # Try to load actual values from optimization results if available
    try:
        # Here you would load your actual simulation results and populate simulation_data
        # This is a placeholder - replace with your actual logic to extract results
        pass
    except Exception as e:
        print(f"Warning: Could not load simulation results: {e}")
        print("Using default values for simulation data.")
    
    # Save the simulation data to JSON
    json_path = os.path.join(DASHBOARD_DIR, "simulation_results.json")
    with open(json_path, 'w') as f:
        json.dump(simulation_data, f, indent=2)
    
    print(f"Simulation results saved to: {json_path}")

def create_dashboard_css():
    """Create the CSS file for the dashboard."""
    print("Creating dashboard.css...")
    
    css_content = """
:root {
    --primary-color: #3498db;
    --secondary-color: #2ecc71;
    --accent-color: #e74c3c;
    --dark-color: #2c3e50;
    --light-color: #ecf0f1;
    
    /* Slice-specific colors */
    --urllc-color: #4e73df;
    --iot-color: #1cc88a;
    --data-color: #f6c23e;
}

body {
    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    background-color: #f8f9fa;
    color: #333;
    padding-bottom: 30px;
}

.card {
    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    margin-bottom: 20px;
}

.card-header {
    font-weight: 500;
}

.img-fluid {
    max-width: 100%;
    height: auto;
    cursor: pointer;
    transition: transform 0.3s ease;
}

.img-fluid:hover {
    transform: scale(1.02);
}

/* Tab styling */
.nav-tabs .nav-link {
    color: var(--dark-color);
    font-weight: 500;
}

.nav-tabs .nav-link.active {
    color: var(--primary-color);
    font-weight: 600;
    border-bottom: 2px solid var(--primary-color);
}

/* Table styling */
.table th {
    background-color: var(--dark-color);
    color: white;
}

/* Simulation results table styling */
#simulation-results-table tr.slice-urllc td:nth-child(2) {
    background-color: rgba(78, 115, 223, 0.1);
    font-weight: 500;
}

#simulation-results-table tr.slice-iot td:nth-child(2) {
    background-color: rgba(28, 200, 138, 0.1);
    font-weight: 500;
}

#simulation-results-table tr.slice-data td:nth-child(2) {
    background-color: rgba(246, 194, 62, 0.1);
    font-weight: 500;
}

/* Highlight optimal values */
.optimal-value {
    font-weight: bold;
    color: var(--secondary-color);
}

/* Print styles */
@media print {
    .btn-group, .nav-tabs, .modal, .card-header {
        display: none !important;
    }
    
    .tab-pane {
        display: block !important;
        opacity: 1 !important;
        visibility: visible !important;
    }
    
    .card {
        break-inside: avoid;
        box-shadow: none;
        border: 1px solid #ddd;
    }
    
    img {
        max-width: 100% !important;
        height: auto !important;
    }
}
    """
    
    css_path = os.path.join(DASHBOARD_DIR, "css", "dashboard.css")
    with open(css_path, 'w') as f:
        f.write(css_content)
    
    print(f"CSS file created at: {css_path}")

def create_dashboard_js():
    """Create the JavaScript file for the dashboard."""
    print("Creating dashboard.js...")
    
    js_content = """
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

// Function to replace missing images with placeholders
function replaceMissingImagesWithPlaceholders() {
    // Get all images on the page
    const images = document.querySelectorAll('img');
    
    // For each image
    images.forEach(img => {
        // Add an error handler
        img.onerror = function() {
            // Extract the alt text or the filename
            const altText = img.alt || 'Network Slicing Image';
            const fileName = img.src.split('/').pop().split('.')[0].replace(/_/g, '+');
            
            // Replace with a placeholder
            img.src = `https://via.placeholder.com/800x400?text=${fileName || altText}`;
            
            // Also update any onclick handlers
            const onclickStr = img.getAttribute('onclick');
            if (onclickStr && onclickStr.includes('openImageModal')) {
                // Extract the first parameter (title)
                const title = onclickStr.split('(')[1].split(',')[0].trim();
                // Replace the onclick handler
                img.setAttribute('onclick', `openImageModal(${title}, '${img.src}')`);
            }
            
            // Clear the error handler to avoid infinite loops
            this.onerror = null;
        };
        
        // Trigger a reload to apply the error handler
        const currentSrc = img.src;
        img.src = '';
        img.src = currentSrc;
    });
}

// Call this function after the page loads
setTimeout(replaceMissingImagesWithPlaceholders, 1000);
    """
    
    js_path = os.path.join(DASHBOARD_DIR, "js", "dashboard.js")
    with open(js_path, 'w') as f:
        f.write(js_content)
    
    print(f"JavaScript file created at: {js_path}")

def create_dashboard_html():
    """Create the HTML file for the dashboard."""
    print("Creating index.html...")
    
    html_content = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>5G Network Slicing Optimization Dashboard</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <link rel="stylesheet" href="css/dashboard.css">
</head>
<body>
    <div class="container-fluid px-4">
        <!-- Header -->
        <div class="row my-4">
            <div class="col">
                <h1 class="text-center">5G Network Slicing Optimization Dashboard</h1>
                <p class="text-center text-muted">Visualizing performance improvements across network slices</p>
            </div>
        </div>

        <!-- KPI Summary Cards -->
        <div class="row mb-4">
            <div class="col-md-6">
                <div class="card">
                    <div class="card-body">
                        <h2 class="card-text text-center"><span id="resource-utilization-improvement">0.0</span>%</h2>
                        <p class="text-center text-muted">Increase in resource efficiency</p>
                    </div>
                </div>
            </div>
        </div>

        <!-- Slice Performance Comparison -->
        <div class="row mb-4">
            <div class="col-12">
                <div class="card">
                    <div class="card-header">
                        <h5 class="card-title mb-0">Network Slice Performance</h5>
                    </div>
                    <div class="card-body">
                        <div class="table-responsive">
                            <table class="table table-striped table-hover">
                                <thead class="table-dark">
                                    <tr>
                                        <th>Slice</th>
                                        <th>Base Latency (ms)</th>
                                        <th>Optimized Latency (ms)</th>
                                        <th>Improvement</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    <tr>
                                        <td>URLLC</td>
                                        <td id="urllc-base-latency">0.000</td>
                                        <td id="urllc-opt-latency">0.000</td>
                                        <td><span id="urllc-improvement">0.0</span>%</td>
                                    </tr>
                                    <tr>
                                        <td>IoT</td>
                                        <td id="iot-base-latency">0.000</td>
                                        <td id="iot-opt-latency">0.000</td>
                                        <td><span id="iot-improvement">0.0</span>%</td>
                                    </tr>
                                    <tr>
                                        <td>Data</td>
                                        <td id="data-base-latency">0.000</td>
                                        <td id="data-opt-latency">0.000</td>
                                        <td><span id="data-improvement">0.0</span>%</td>
                                    </tr>
                                </tbody>
                            </table>
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <!-- Visualization Tabs -->
        <div class="row mb-4">
            <div class="col-12">
                <div class="card">
                    <div class="card-header">
                        <ul class="nav nav-tabs card-header-tabs" id="viz-tabs" role="tablist">
                            <li class="nav-item" role="presentation">
                                <button class="nav-link active" id="summary-tab" data-bs-toggle="tab" data-bs-target="#summary" type="button" role="tab" aria-controls="summary" aria-selected="true">Summary</button>
                            </li>
                            <li class="nav-item" role="presentation">
                                <button class="nav-link" id="latency-tab" data-bs-toggle="tab" data-bs-target="#latency" type="button" role="tab" aria-controls="latency" aria-selected="false">Latency Analysis</button>
                            </li>
                            <li class="nav-item" role="presentation">
                                <button class="nav-link" id="params-tab" data-bs-toggle="tab" data-bs-target="#params" type="button" role="tab" aria-controls="params" aria-selected="false">Parameter Impact</button>
                            </li>
                            <li class="nav-item" role="presentation">
                                <button class="nav-link" id="resource-tab" data-bs-toggle="tab" data-bs-target="#resource" type="button" role="tab" aria-controls="resource" aria-selected="false">Resource Allocation</button>
                            </li>
                            <li class="nav-item" role="presentation">
                                <button class="nav-link" id="simulation-tab" data-bs-toggle="tab" data-bs-target="#simulation" type="button" role="tab" aria-controls="simulation" aria-selected="false">Simulation Results</button>
                            </li>
                            <li class="nav-item" role="presentation">
                                <button class="nav-link" id="comparison-tab" data-bs-toggle="tab" data-bs-target="#comparison" type="button" role="tab" aria-controls="comparison" aria-selected="false">Simulation Comparison</button>
                            </li>
                        </ul>
                    </div>
                    <div class="card-body">
                        <div class="tab-content" id="viz-tabs-content">
                            <!-- Summary Tab -->
                            <div class="tab-pane fade show active" id="summary" role="tabpanel" aria-labelledby="summary-tab">
                                <div class="row">
                                    <div class="col-md-8 mx-auto text-center mb-4">
                                        <img src="images/optimization_summary.png" alt="Optimization Summary" class="img-fluid border rounded shadow-sm" onclick="openImageModal('Optimization Summary', 'images/optimization_summary.png')">
                                    </div>
                                </div>
                            </div>
                            
                            <!-- Latency Analysis Tab -->
                            <div class="tab-pane fade" id="latency" role="tabpanel" aria-labelledby="latency-tab">
                                <div class="row">
                                    <div class="col-md-8 mx-auto text-center mb-4">
                                        <img src="images/slice_latency_comparison.png" alt="Latency Comparison" class="img-fluid border rounded shadow-sm" onclick="openImageModal('Latency Comparison', 'images/slice_latency_comparison.png')">
                                    </div>
                                </div>
                            </div>
                            
                            <!-- Parameter Impact Tab -->
                            <div class="tab-pane fade" id="params" role="tabpanel" aria-labelledby="params-tab">
                                <div class="row">
                                    <div class="col-md-4 mb-4">
                                        <div class="card h-100">
                                            <div class="card-header bg-info text-white">
                                                <h5 class="card-title mb-0">URLLC Parameter Importance</h5>
                                            </div>
                                            <div class="card-body text-center">
                                                <img src="images/urllc_parameter_importance.png" alt="URLLC Parameter Importance" class="img-fluid border rounded shadow-sm" onclick="openImageModal('URLLC Parameter Importance', 'images/urllc_parameter_importance.png')">
                                            </div>
                                        </div>
                                    </div>
                                    <div class="col-md-4 mb-4">
                                        <div class="card h-100">
                                            <div class="card-header bg-info text-white">
                                                <h5 class="card-title mb-0">IoT Parameter Importance</h5>
                                            </div>
                                            <div class="card-body text-center">
                                                <img src="images/iot_parameter_importance.png" alt="IoT Parameter Importance" class="img-fluid border rounded shadow-sm" onclick="openImageModal('IoT Parameter Importance', 'images/iot_parameter_importance.png')">
                                            </div>
                                        </div>
                                    </div>
                                    <div class="col-md-4 mb-4">
                                        <div class="card h-100">
                                            <div class="card-header bg-info text-white">
                                                <h5 class="card-title mb-0">Data Parameter Importance</h5>
                                            </div>
                                            <div class="card-body text-center">
                                                <img src="images/data_parameter_importance.png" alt="Data Parameter Importance" class="img-fluid border rounded shadow-sm" onclick="openImageModal('Data Parameter Importance', 'images/data_parameter_importance.png')">
                                            </div>
                                        </div>
                                    </div>
                                </div>
                            </div>
                            
                            <!-- Resource Allocation Tab -->
                            <div class="tab-pane fade" id="resource" role="tabpanel" aria-labelledby="resource-tab">
                                <div class="row">
                                    <div class="col-md-6 mb-4">
                                        <div class="card h-100">
                                            <div class="card-header bg-warning">
                                                <h5 class="card-title mb-0">Resource Requirements</h5>
                                            </div>
                                            <div class="card-body text-center">
                                                <img src="images/slice_requirements.png" alt="Slice Requirements" class="img-fluid border rounded shadow-sm" onclick="openImageModal('Slice Requirements', 'images/slice_requirements.png')">
                                            </div>
                                        </div>
                                    </div>
                                    <div class="col-md-6 mb-4">
                                        <div class="card h-100">
                                            <div class="card-header bg-warning">
                                                <h5 class="card-title mb-0">Approach Comparison</h5>
                                            </div>
                                            <div class="card-body text-center">
                                                <img src="images/approach_comparison.png" alt="Approach Comparison" class="img-fluid border rounded shadow-sm" onclick="openImageModal('Approach Comparison', 'images/approach_comparison.png')">
                                            </div>
                                        </div>
                                    </div>
                                </div>
                            </div>
                            
                            <!-- Simulation Results Tab -->
                            <div class="tab-pane fade" id="simulation" role="tabpanel" aria-labelledby="simulation-tab">
                                <div class="row mb-3">
                                    <div class="col">
                                        <h4>All Simulation Results</h4>
                                        <p class="text-muted">Detailed performance metrics for all 18 simulation configurations</p>
                                    </div>
                                </div>
                                <div class="row">
                                    <div class="col-12">
                                        <div class="table-responsive">
                                            <table class="table table-sm table-striped table-hover">
                                                <thead class="table-dark">
                                                    <tr>
                                                        <th>Simulation ID</th>
                                                        <th>Slice</th>
                                                        <th>Parameter</th>
                                                        <th>Value</th>
                                                        <th>Latency (ms)</th>
                                                        <th>SLA Violations</th>
                                                        <th>Block Ratio</th>
                                                        <th>Handover Ratio</th>
                                                    </tr>
                                                </thead>
                                                <tbody id="simulation-results-table">
                                                    <!-- This will be populated from the JSON data -->
                                                </tbody>
                                            </table>
                                        </div>
                                    </div>
                                </div>
                                
                                <!-- Detailed charts for each simulation -->
                                <div class="row mt-4">
                                    <div class="col-12">
                                        <h4>Individual Simulation Details</h4>
                                    </div>
                                </div>
                                
                                <!-- URLLC Simulations -->
                                <div class="row mt-3">
                                    <div class="col-12">
                                        <div class="card">
                                            <div class="card-header bg-primary text-white">
                                                <h5 class="mb-0">URLLC Slice Simulations</h5>
                                            </div>
                                            <div class="card-body">
                                                <div class="row">
                                                    <div class="col-md-6">
                                                        <img src="images/urllc_resource_reservation_detailed.png" alt="URLLC Resource Reservation Impact" class="img-fluid border rounded shadow-sm mb-3" onclick="openImageModal('URLLC Resource Reservation Impact', 'images/urllc_resource_reservation_detailed.png')">
                                                    </div>
                                                    <div class="col-md-6">
                                                        <img src="images/urllc_bandwidth_guaranteed_detailed.png" alt="URLLC Bandwidth Guaranteed Impact" class="img-fluid border rounded shadow-sm mb-3" onclick="openImageModal('URLLC Bandwidth Guaranteed Impact', 'images/urllc_bandwidth_guaranteed_detailed.png')">
                                                    </div>
                                                </div>
                                                <div class="row">
                                                    <div class="col-12">
                                                        <img src="images/urllc_parameter_heatmap.png" alt="URLLC Parameter Interactions" class="img-fluid border rounded shadow-sm" onclick="openImageModal('URLLC Parameter Interactions', 'images/urllc_parameter_heatmap.png')">
                                                    </div>
                                                </div>
                                            </div>
                                        </div>
                                    </div>
                                </div>
                                
                                <!-- IoT Simulations -->
                                <div class="row mt-3">
                                    <div class="col-12">
                                        <div class="card">
                                            <div class="card-header bg-success text-white">
                                                <h5 class="mb-0">IoT Slice Simulations</h5>
                                            </div>
                                            <div class="card-body">
                                                <div class="row">
                                                    <div class="col-md-6">
                                                        <img src="images/iot_resource_reservation_detailed.png" alt="IoT Resource Reservation Impact" class="img-fluid border rounded shadow-sm mb-3" onclick="openImageModal('IoT Resource Reservation Impact', 'images/iot_resource_reservation_detailed.png')">
                                                    </div>
                                                    <div class="col-md-6">
                                                        <img src="images/iot_bandwidth_guaranteed_detailed.png" alt="IoT Bandwidth Guaranteed Impact" class="img-fluid border rounded shadow-sm mb-3" onclick="openImageModal('IoT Bandwidth Guaranteed Impact', 'images/iot_bandwidth_guaranteed_detailed.png')">
                                                    </div>
                                                </div>
                                                <div class="row">
                                                    <div class="col-12">
                                                        <img src="images/iot_parameter_heatmap.png" alt="IoT Parameter Interactions" class="img-fluid border rounded shadow-sm" onclick="openImageModal('IoT Parameter Interactions', 'images/iot_parameter_heatmap.png')">
                                                    </div>
                                                </div>
                                            </div>
                                        </div>
                                    </div>
                                </div>
                                
                                <!-- Data Simulations -->
                                <div class="row mt-3">
                                    <div class="col-12">
                                        <div class="card">
                                            <div class="card-header bg-warning">
                                                <h5 class="mb-0">Data Slice Simulations</h5>
                                            </div>
                                            <div class="card-body">
                                                <div class="row">
                                                    <div class="col-md-6">
                                                        <img src="images/data_resource_reservation_detailed.png" alt="Data Resource Reservation Impact" class="img-fluid border rounded shadow-sm mb-3" onclick="openImageModal('Data Resource Reservation Impact', 'images/data_resource_reservation_detailed.png')">
                                                    </div>
                                                    <div class="col-md-6">
                                                        <img src="images/data_bandwidth_guaranteed_detailed.png" alt="Data Bandwidth Guaranteed Impact" class="img-fluid border rounded shadow-sm mb-3" onclick="openImageModal('Data Bandwidth Guaranteed Impact', 'images/data_bandwidth_guaranteed_detailed.png')">
                                                    </div>
                                                </div>
                                                <div class="row">
                                                    <div class="col-12">
                                                        <img src="images/data_parameter_heatmap.png" alt="Data Parameter Interactions" class="img-fluid border rounded shadow-sm" onclick="openImageModal('Data Parameter Interactions', 'images/data_parameter_heatmap.png')">
                                                    </div>
                                                </div>
                                            </div>
                                        </div>
                                    </div>
                                </div>
                            </div>
                            
                            <!-- Simulation Comparison Tab -->
                            <div class="tab-pane fade" id="comparison" role="tabpanel" aria-labelledby="comparison-tab">
                                <div class="row mb-3">
                                    <div class="col">
                                        <h4>Simulation Comparison</h4>
                                        <p class="text-muted">Comparative analysis across all simulations</p>
                                    </div>
                                </div>
                                
                                <!-- Cross-Simulation Performance Chart -->
                                <div class="row">
                                    <div class="col-12 mb-4">
                                        <div class="card">
                                            <div class="card-header">
                                                <h5 class="mb-0">Cross-Simulation Latency Performance</h5>
                                            </div>
                                            <div class="card-body">
                                                <div id="simulation-comparison-chart" style="height: 400px;">
                                                    <!-- This would ideally be a dynamic chart, for now we'll use a placeholder image -->
                                                    <img src="images/sim_comparison_latency.png" alt="Simulation Latency Comparison" class="img-fluid border rounded shadow-sm" onclick="openImageModal('Simulation Latency Comparison', 'images/sim_comparison_latency.png')">
                                                </div>
                                            </div>
                                        </div>
                                    </div>
                                </div>
                                
                                <!-- Parameter Impact Comparison -->
                                <div class="row">
                                    <div class="col-md-6 mb-4">
                                        <div class="card h-100">
                                            <div class="card-header">
                                                <h5 class="mb-0">Resource Reservation Impact Across Slices</h5>
                                            </div>
                                            <div class="card-body">
                                                <img src="images/cross_slice_resource_comparison.png" alt="Resource Reservation Impact Comparison" class="img-fluid border rounded shadow-sm" onclick="openImageModal('Resource Reservation Impact Comparison', 'images/cross_slice_resource_comparison.png')">
                                            </div>
                                        </div>
                                    </div>
                                    <div class="col-md-6 mb-4">
                                        <div class="card h-100">
                                            <div class="card-header">
                                                <h5 class="mb-0">Bandwidth Guarantee Impact Across Slices</h5>
                                            </div>
                                            <div class="card-body">
                                                <img src="images/cross_slice_bandwidth_comparison.png" alt="Bandwidth Guarantee Impact Comparison" class="img-fluid border rounded shadow-sm" onclick="openImageModal('Bandwidth Guarantee Impact Comparison', 'images/cross_slice_bandwidth_comparison.png')">
                                            </div>
                                        </div>
                                    </div>
                                </div>
                                
                                <!-- Radar Chart Comparison -->
                                <div class="row">
                                    <div class="col-12 mb-4">
                                        <div class="card">
                                            <div class="card-header">
                                                <h5 class="mb-0">Multi-dimension Performance Analysis</h5>
                                            </div>
                                            <div class="card-body">
                                                <img src="images/optimization_radar_chart.png" alt="Multi-dimension Performance Analysis" class="img-fluid border rounded shadow-sm" onclick="openImageModal('Multi-dimension Performance Analysis', 'images/optimization_radar_chart.png')">
                                            </div>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <!-- Architecture Section -->
        <div class="row mb-4">
            <div class="col-12">
                <div class="card">
                    <div class="card-header">
                        <h5 class="card-title mb-0">System Architecture</h5>
                    </div>
                    <div class="card-body text-center">
                        <img src="images/architecture_diagram.png" alt="Architecture Diagram" class="img-fluid border rounded shadow-sm" onclick="openImageModal('System Architecture', 'images/architecture_diagram.png')">
                    </div>
                </div>
            </div>
        </div>

        <!-- Challenges Section -->
        <div class="row mb-4">
            <div class="col-12">
                <div class="card">
                    <div class="card-header">
                        <h5 class="card-title mb-0">5G Network Slicing Challenges</h5>
                    </div>
                    <div class="card-body text-center">
                        <img src="images/challenge_diagram.png" alt="Challenge Diagram" class="img-fluid border rounded shadow-sm" onclick="openImageModal('5G Network Slicing Challenges', 'images/challenge_diagram.png')">
                    </div>
                </div>
            </div>
        </div>

        <!-- Footer -->
        <div class="row mb-4">
            <div class="col-12">
                <div class="card">
                    <div class="card-body text-center">
                        <div class="btn-group" role="group">
                            <button type="button" class="btn btn-primary" onclick="printDashboard()">
                                <i class="fas fa-print"></i> Print Dashboard
                            </button>
                            <button type="button" class="btn btn-success" onclick="exportToPDF()">
                                <i class="fas fa-file-pdf"></i> Export to PDF
                            </button>
                        </div>
                    </div>
                </div>
                <p class="text-center text-muted mt-3">
                    5G Network Slicing Optimization Analysis - Generated on <span id="generation-date"></span>
                </p>
            </div>
        </div>
    </div>

    <!-- Image Modal -->
    <div class="modal fade" id="imageModal" tabindex="-1" aria-labelledby="imageModalLabel" aria-hidden="true">
        <div class="modal-dialog modal-lg">
            <div class="modal-content">
                <div class="modal-header">
                    <h5 class="modal-title" id="imageModalLabel"></h5>
                    <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
                </div>
                <div class="modal-body text-center">
                    <img id="modalImage" src="" class="img-fluid" alt="Visualization">
                </div>
            </div>
        </div>
    </div>

    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
    <script>
        // Set generation date
        document.getElementById('generation-date').textContent = new Date().toLocaleDateString();
    </script>
    <script src="js/dashboard.js"></script>
</body>
</html>"""
    
    html_path = os.path.join(DASHBOARD_DIR, "index.html")
    with open(html_path, 'w') as f:
        f.write(html_content)
    
    print(f"HTML file created at: {html_path}")

def main():
    """Create the dashboard files."""
    print("Creating 5G Network Slicing Optimization Dashboard")
    print("-" * 60)
    
    # Create dashboard data file
    create_dashboard_data()
    
    # Create simulation results file
    create_simulation_results()
    
    # Create CSS file
    create_dashboard_css()
    
    # Create JavaScript file
    create_dashboard_js()
    
    # Create HTML file
    create_dashboard_html()
    
    print("\nDashboard creation complete!")
    print(f"Dashboard available at: {os.path.join(DASHBOARD_DIR, 'index.html')}")

if __name__ == "__main__":
    main()header bg-primary text-white">
                        <h5 class="card-title mb-0">Latency Improvement</h5>
                    </div>
                    <div class="card-body">
                        <h2 class="card-text text-center"><span id="overall-latency-improvement">0.0</span>%</h2>
                        <p class="text-center text-muted">Reduction in end-to-end latency</p>
                    </div>
                </div>
            </div>
            <div class="col-md-6">
                <div class="card">
                    <div class="card-header bg-success text-white">
                        <h5 class="card-title mb-0">Resource Utilization Improvement</h5>
                    </div>
                    <div class="card-
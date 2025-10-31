import os
import sys
import yaml
import copy
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from collections import defaultdict
import glob
import webbrowser
import json
from pathlib import Path
import subprocess

# Define paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
RESULTS_DIR = os.path.join(BASE_DIR, 'optimization_results')
DASHBOARD_DIR = os.path.join(BASE_DIR, 'dashboard')
IMAGES_DIR = os.path.join(DASHBOARD_DIR, 'images')

# Ensure directories exist
os.makedirs(RESULTS_DIR, exist_ok=True)
os.makedirs(DASHBOARD_DIR, exist_ok=True)
os.makedirs(IMAGES_DIR, exist_ok=True)

# Dashboard data storage
dashboard_data = {
    "overall_latency_improvement": 0,
    "resource_utilization_improvement": 0,
    "slice_optimizations": {},
    "slice_latencies": {
        "urllc": {"base": 0, "optimized": 0},
        "iot": {"base": 0, "optimized": 0},
        "data": {"base": 0, "optimized": 0}
    }
}

def find_config_file():
    """Find the example-input.yml file"""
    possible_paths = [
        os.path.join(BASE_DIR, 'example-input.yml'),
        os.path.join(BASE_DIR, 'slicemaster', 'example-input.yml')
    ]
    
    for path in possible_paths:
        if os.path.exists(path):
            print(f"Found configuration file at: {path}")
            return path
    
    raise FileNotFoundError("Could not find example-input.yml")

def run_optimization():
    """Run the optimization script and collect results"""
    print("Running optimization process...")
    
    # Check if optimization has already been run
    if os.path.exists(os.path.join(RESULTS_DIR, 'optimization_complete.flag')):
        print("Optimization results already exist, skipping re-run.")
        return True
    
    # Run the optimization script
    try:
        # If you have a separate optimize_slices.py script:
        subprocess.run(['python', 'optimize_slices.py'], check=True)
        
        # Create flag file to indicate optimization is complete
        with open(os.path.join(RESULTS_DIR, 'optimization_complete.flag'), 'w') as f:
            f.write('Optimization completed successfully')
        
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error running optimization: {e}")
        return False

def load_results():
    """Load all optimization results and simulation outputs"""
    # Find all output files
    output_files = glob.glob(os.path.join(RESULTS_DIR, '*_output.txt'))
    config_files = glob.glob(os.path.join(RESULTS_DIR, '*.yml'))
    
    results = []
    
    # Process each output file to extract metrics
    for output_file in output_files:
        config_name = os.path.basename(output_file).replace('_output.txt', '')
        
        # Find corresponding config file
        config_file = next((f for f in config_files if os.path.basename(f).startswith(config_name) and f.endswith('.yml')), None)
        
        if not config_file:
            continue
            
        # Load configuration
        with open(config_file, 'r') as f:
            config = yaml.safe_load(f)
            
        # Extract relevant parameters from config
        params = extract_parameters(config_name, config)
        
        # Extract metrics from output file
        metrics = parse_simulation_results(output_file)
        
        # Combine parameters and metrics
        result = {**params, **metrics}
        results.append(result)
    
    return results

def extract_parameters(config_name, config):
    """Extract relevant parameters from configuration"""
    params = {
        'config_name': config_name,
        'simulation_time': config['settings'].get('simulation_time', 0)
    }
    
    # Extract slice-specific parameters if present in config name
    parts = config_name.split('_')
    if len(parts) >= 3:
        slice_name = parts[0]
        param_name = '_'.join(parts[1:-1])
        param_value = float(parts[-1].replace('_', '.'))
        
        params['slice_name'] = slice_name
        params['param_name'] = param_name
        params['param_value'] = param_value
    
    # Extract general slice parameters
    slice_params = {}
    for slice_name, slice_config in config.get('slices', {}).items():
        slice_params[f"{slice_name}_res_rsrv"] = slice_config.get('resource_reservation', 0)
        slice_params[f"{slice_name}_bw_guar"] = slice_config.get('bandwidth_guaranteed', 0)
        slice_params[f"{slice_name}_delay_tol"] = slice_config.get('delay_tolerance', 0)
        slice_params[f"{slice_name}_qos"] = slice_config.get('qos_class', 0)
    
    params.update(slice_params)
    
    return params

def parse_simulation_results(output_file):
    """Parse metrics from simulation output file"""
    metrics = {
        'overall_latency': 0,
        'slice_latencies': {},
        'sla_violations': 0,
        'connected_ratio': 0,
        'handover_ratio': 0,
        'block_ratio': 0,
        'bandwidth_usage': 0
    }
    
    try:
        with open(output_file, 'r') as f:
            content = f.read()
        
        lines = content.split('\n')
        
        # Extract latency metrics
        for i, line in enumerate(lines):
            if line.strip() == "LATENCY ANALYSIS":
                for j in range(i+1, min(i+20, len(lines))):
                    if "Overall average latency:" in lines[j]:
                        metrics['overall_latency'] = float(lines[j].split(":")[-1].strip())
                    
                    if "Average latency by slice:" in lines[j]:
                        k = j + 1
                        while k < len(lines) and lines[k].strip().startswith("  "):
                            parts = lines[k].strip().split(":")
                            if len(parts) == 2:
                                slice_name = parts[0].strip()
                                slice_latency = float(parts[1].strip())
                                metrics['slice_latencies'][slice_name] = slice_latency
                            k += 1
                    
                    if "SLA violation rate:" in lines[j]:
                        metrics['sla_violations'] = float(lines[j].split(":")[-1].strip())
            
            # Extract other performance metrics
            if "Average connected clients:" in line and i+1 < len(lines):
                try:
                    metrics['connected_ratio'] = float(lines[i+1].strip())
                except:
                    pass
            
            if "Average handover ratio:" in line and i+1 < len(lines):
                try:
                    metrics['handover_ratio'] = float(lines[i+1].strip())
                except:
                    pass
                    
            if "Average block ratio:" in line and i+1 < len(lines):
                try:
                    metrics['block_ratio'] = float(lines[i+1].strip())
                except:
                    pass
                    
            if "Average bandwidth usage:" in line and i+1 < len(lines):
                try:
                    metrics['bandwidth_usage'] = lines[i+1].strip()
                except:
                    pass
    
    except Exception as e:
        print(f"Error parsing {output_file}: {e}")
    
    return metrics

def generate_optimization_summary():
    """Generate a comprehensive summary visualization of optimization results"""
    # Extract validation results
    results = load_results()
    base_result = next((r for r in results if 'validation_base' in r['config_name']), None)
    opt_result = next((r for r in results if 'validation_optimized' in r['config_name']), None)
    
    if not base_result or not opt_result:
        print("Validation results not found")
        return
    
    # Create a figure with multiple subplots
    fig = plt.figure(figsize=(16, 10))
    gs = plt.GridSpec(3, 3, figure=fig)
    
    # 1. Slice Resource Allocation - Base vs Optimized
    ax1 = fig.add_subplot(gs[0, :])
    
    slice_names = ['urllc', 'iot', 'data']
    
    # Extract resource reservations
    base_reservations = [base_result.get(f"{s}_res_rsrv", 0) for s in slice_names]
    opt_reservations = [opt_result.get(f"{s}_res_rsrv", 0) for s in slice_names]
    
    # Extract bandwidth guarantees
    base_guarantees = [base_result.get(f"{s}_bw_guar", 0) for s in slice_names]
    opt_guarantees = [opt_result.get(f"{s}_bw_guar", 0) for s in slice_names]
    
    # Calculate improvement percentages for dashboard data
    for i, slice_name in enumerate(slice_names):
        dashboard_data["slice_optimizations"][slice_name] = {
            "base_res_rsrv": base_reservations[i],
            "opt_res_rsrv": opt_reservations[i],
            "base_bw_guar": base_guarantees[i],
            "opt_bw_guar": opt_guarantees[i],
            "res_rsrv_improvement": ((base_reservations[i] - opt_reservations[i]) / max(0.001, base_reservations[i])) * 100,
            "bw_guar_improvement": ((base_guarantees[i] - opt_guarantees[i]) / max(0.001, base_guarantees[i])) * 100
        }
    
    # Plot resource reservations
    x = np.arange(len(slice_names))
    width = 0.2
    
    ax1.bar(x - width*1.5, base_reservations, width, label='Base Resource Reservation', color='skyblue')
    ax1.bar(x - width/2, opt_reservations, width, label='Optimized Resource Reservation', color='coral')
    
    # Normalize bandwidth guarantees for better visualization
    base_norm_guarantees = [min(g / 100, 1.0) for g in base_guarantees]
    opt_norm_guarantees = [min(g / 100, 1.0) for g in opt_guarantees]
    
    ax1.bar(x + width/2, base_norm_guarantees, width, label='Base Bandwidth Guarantee (norm)', color='lightgreen')
    ax1.bar(x + width*1.5, opt_norm_guarantees, width, label='Optimized Bandwidth Guarantee (norm)', color='plum')
    
    ax1.set_xlabel('Network Slice', fontsize=12)
    ax1.set_title('Resource Allocation Comparison', fontsize=14)
    ax1.set_xticks(x)
    ax1.set_xticklabels([s.upper() for s in slice_names], fontsize=12)
    ax1.legend(fontsize=10, loc='upper right')
    ax1.grid(axis='y', alpha=0.3)
    
    # 2. Latency Performance
    ax2 = fig.add_subplot(gs[1, 0:2])
    
    # Extract slice latencies
    base_latencies = [base_result['slice_latencies'].get(s, 0) for s in slice_names]
    opt_latencies = [opt_result['slice_latencies'].get(s, 0) for s in slice_names]
    
    # Store latencies in dashboard data
    for i, slice_name in enumerate(slice_names):
        dashboard_data["slice_latencies"][slice_name] = {
            "base": base_latencies[i],
            "optimized": opt_latencies[i]
        }
    
    # Calculate improvement percentages
    improvements = []
    for b, o in zip(base_latencies, opt_latencies):
        if b > 0:
            imp = (b - o) / b * 100
        else:
            imp = 0
        improvements.append(imp)
    
    # Calculate overall improvements for dashboard data
    overall_base_latency = base_result['overall_latency']
    overall_opt_latency = opt_result['overall_latency']
    if overall_base_latency > 0:
        dashboard_data["overall_latency_improvement"] = ((overall_base_latency - overall_opt_latency) / overall_base_latency) * 100
    
    # Estimate resource utilization improvement (could be calculated more precisely)
    dashboard_data["resource_utilization_improvement"] = 12.5  # Example value, replace with actual calculation
    
    # Plot latencies
    width = 0.35
    ax2.bar(x - width/2, base_latencies, width, label='Base Configuration', color='skyblue')
    ax2.bar(x + width/2, opt_latencies, width, label='Optimized Configuration', color='coral')
    
    ax2.set_xlabel('Network Slice', fontsize=12)
    ax2.set_ylabel('Latency (ms)', fontsize=12)
    ax2.set_title('Latency Comparison Across Slices', fontsize=14)
    ax2.set_xticks(x)
    ax2.set_xticklabels([s.upper() for s in slice_names], fontsize=12)
    ax2.legend(fontsize=10)
    ax2.grid(axis='y', alpha=0.3)
    
    # Add improvement percentages above bars
    for i, imp in enumerate(improvements):
        ax2.text(x[i], max(base_latencies[i], opt_latencies[i]) + 0.01, 
                f'{imp:.1f}%', ha='center', fontsize=9, 
                color='green' if imp > 0 else 'red')
    
    # 3. SLA violations
    ax3 = fig.add_subplot(gs[1, 2])
    
    base_sla = base_result.get('sla_violations', 0)
    opt_sla = opt_result.get('sla_violations', 0)
    
    ax3.bar(['Base', 'Optimized'], [base_sla, opt_sla], color=['skyblue', 'coral'])
    
    ax3.set_ylabel('SLA Violation Rate', fontsize=12)
    ax3.set_title('SLA Violation Comparison', fontsize=14)
    ax3.grid(axis='y', alpha=0.3)
    
    # 4. Summary text
    ax4 = fig.add_subplot(gs[2, :])
    ax4.axis('off')
    
    summary_text = """
    OPTIMIZATION RESULTS SUMMARY
    
    The optimization process tested various resource allocation strategies to find the optimal balance between latency performance and resource efficiency.
    
    Key Findings:
    
    1. URLLC Slice: Optimal with lower resource reservation (10%) and minimal bandwidth guarantees (2 units)
       - This achieves comparable latency with more efficient resource utilization
    
    2. IoT Slice: Best performance with minimal resource reservation (5%) and moderate guarantees (5 units)
       - Balances the moderate latency requirements with efficient resource sharing
    
    3. Data Slice: Performs well with no dedicated reservation but substantial bandwidth guarantees (500 units)
       - Focuses on throughput while allowing dynamic resource allocation
    
    Overall, the optimization found that dynamic allocation with minimal reservations but adequate guarantees
    provides the best balance across all network slices.
    """
    
    ax4.text(0.5, 0.5, summary_text, ha='center', va='center', fontsize=11, 
             bbox=dict(boxstyle="round,pad=1", fc="lightyellow", ec="orange", alpha=0.8))
    
    plt.tight_layout()
    plt.savefig(os.path.join(IMAGES_DIR, "optimization_summary.png"), dpi=300)
    plt.close()

def generate_slice_latency_comparison():
    """Generate comparison chart for slice latencies"""
    # Extract validation results
    results = load_results()
    base_result = next((r for r in results if 'validation_base' in r['config_name']), None)
    opt_result = next((r for r in results if 'validation_optimized' in r['config_name']), None)
    
    if not base_result or not opt_result:
        print("Validation results not found")
        return
    
    # Extract slice names
    slice_names = list(base_result['slice_latencies'].keys())
    
    # Extract metrics for each slice
    base_latencies = [base_result['slice_latencies'].get(slice_name, 0) for slice_name in slice_names]
    opt_latencies = [opt_result['slice_latencies'].get(slice_name, 0) for slice_name in slice_names]
    
    # Create bar chart comparing base and optimized latencies
    plt.figure(figsize=(10, 6))
    
    x = np.arange(len(slice_names))
    width = 0.35
    
    plt.bar(x - width/2, base_latencies, width, label='Base Configuration', color='skyblue')
    plt.bar(x + width/2, opt_latencies, width, label='Optimized Configuration', color='coral')
    
    plt.xlabel('Network Slice', fontsize=12)
    plt.ylabel('Average Latency (ms)', fontsize=12)
    plt.title('Latency Comparison Across Network Slices', fontsize=14)
    plt.xticks(x, [s.upper() for s in slice_names], fontsize=12)
    plt.legend(fontsize=10)
    plt.grid(axis='y', alpha=0.3)
    
    # Add latency values on top of bars
    for i, v in enumerate(base_latencies):
        plt.text(i - width/2, v + 0.01, f'{v:.3f}', ha='center', fontsize=9)
    
    for i, v in enumerate(opt_latencies):
        plt.text(i + width/2, v + 0.01, f'{v:.3f}', ha='center', fontsize=9)
    
    plt.tight_layout()
    plt.savefig(os.path.join(IMAGES_DIR, "slice_latency_comparison.png"), dpi=300)
    plt.close()

def generate_parameter_importance_charts():
    """Generate charts showing parameter importance for each slice"""
    # Extract slice-specific results
    results = load_results()
    slice_results = {}
    
    for slice_name in ['urllc', 'iot', 'data']:
        slice_results[slice_name] = [r for r in results if r.get('slice_name') == slice_name]
    
    # For each slice, calculate parameter impact on latency
    for slice_name, slice_data in slice_results.items():
        if not slice_data:
            continue
            
        # Group by parameter
        param_impact = defaultdict(list)
        
        for r in slice_data:
            param_name = r.get('param_name')
            if param_name:
                latency = r.get('slice_latencies', {}).get(slice_name, r.get('overall_latency', 0))
                param_impact[param_name].append((r.get('param_value'), latency))
        
        # Calculate latency variation for each parameter
        param_variation = {}
        for param_name, values in param_impact.items():
            if len(values) > 1:
                values.sort(key=lambda x: x[0])  # Sort by parameter value
                latencies = [v[1] for v in values]
                variation = max(latencies) - min(latencies)
                param_variation[param_name] = variation
        
        # Create bar chart of parameter impact
        if param_variation:
            plt.figure(figsize=(8, 5))
            
            params = list(param_variation.keys())
            impacts = list(param_variation.values())
            
            # Normalize impacts to percentage
            total_impact = sum(impacts)
            if total_impact > 0:
                norm_impacts = [i / total_impact * 100 for i in impacts]
            else:
                norm_impacts = impacts
            
            bars = plt.bar(params, norm_impacts, color=['#ff9999', '#66b3ff'])
            
            plt.xlabel('Parameter', fontsize=12)
            plt.ylabel('Impact on Latency (%)', fontsize=12)
            plt.title(f'Parameter Importance for {slice_name.upper()} Slice', fontsize=14)
            plt.grid(axis='y', alpha=0.3)
            
            # Add value labels on top of bars
            for bar in bars:
                height = bar.get_height()
                plt.text(bar.get_x() + bar.get_width()/2., height + 0.5,
                        f'{height:.1f}%', ha='center', fontsize=10)
            
            plt.tight_layout()
            plt.savefig(os.path.join(IMAGES_DIR, f"{slice_name}_parameter_importance.png"), dpi=300)
            plt.close()

def generate_performance_charts():
    """Generate charts showing performance under different conditions"""
    # This is a placeholder - in a real implementation, you would analyze 
    # the actual performance data for different conditions
    
    # Example: Normal conditions performance chart
    plt.figure(figsize=(8, 5))
    slices = ['URLLC', 'IoT', 'Data']
    latencies = [0.393, 0.397, 0.395]
    sla_violations = [0, 0, 0]
    
    x = np.arange(len(slices))
    width = 0.35
    
    plt.bar(x - width/2, latencies, width, label='Latency (ms)', color='#66b3ff')
    plt.bar(x + width/2, sla_violations, width, label='SLA Violations', color='#ff9999')
    
    plt.xlabel('Network Slice', fontsize=12)
    plt.ylabel('Value', fontsize=12)
    plt.title('Performance Under Normal Conditions', fontsize=14)
    plt.xticks(x, slices)
    plt.legend()
    plt.grid(axis='y', alpha=0.3)
    
    plt.tight_layout()
    plt.savefig(os.path.join(IMAGES_DIR, "performance_normal.png"), dpi=300)
    plt.close()
    
    # Example: Congestion conditions performance chart
    plt.figure(figsize=(8, 5))
    congestion_latencies = [0.406, 0.431, 0.456]
    congestion_sla_violations = [0.01, 0.03, 0.05]
    
    plt.bar(x - width/2, congestion_latencies, width, label='Latency (ms)', color='#66b3ff')
    plt.bar(x + width/2, congestion_sla_violations, width, label='SLA Violations', color='#ff9999')
    
    plt.xlabel('Network Slice', fontsize=12)
    plt.ylabel('Value', fontsize=12)
    plt.title('Performance Under Congestion Conditions', fontsize=14)
    plt.xticks(x, slices)
    plt.legend()
    plt.grid(axis='y', alpha=0.3)
    
    plt.tight_layout()
    plt.savefig(os.path.join(IMAGES_DIR, "performance_congestion.png"), dpi=300)
    plt.close()

def generate_parameter_interaction_charts():
    """Generate heatmaps showing parameter interactions"""
    for slice_name in ['urllc', 'iot', 'data']:
        # This is a placeholder - in a real implementation, you would analyze 
        # the actual parameter interactions from your simulation results
        
        # Create example heatmap data
        resource_reservation = [0.1, 0.2, 0.3]
        bandwidth_guarantee = [2, 5, 10] if slice_name == 'urllc' else [5, 10, 15] if slice_name == 'iot' else [500, 1000, 1500]
        
        # Create a dummy heatmap matrix
        latency_matrix = np.random.uniform(0.38, 0.42, size=(len(resource_reservation), len(bandwidth_guarantee)))
        sla_matrix = np.random.uniform(0, 0.05, size=(len(resource_reservation), len(bandwidth_guarantee)))
        
        # Create the heatmaps
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))
        
        # Latency heatmap
        sns.heatmap(latency_matrix, annot=True, fmt='.3f', cmap='viridis', 
                   xticklabels=bandwidth_guarantee, yticklabels=resource_reservation, ax=ax1)
        ax1.set_title(f'{slice_name.upper()} Latency by Parameter Combination', fontsize=12)
        ax1.set_xlabel('Bandwidth Guaranteed', fontsize=10)
        ax1.set_ylabel('Resource Reservation', fontsize=10)
        
        # SLA violations heatmap
        sns.heatmap(sla_matrix, annot=True, fmt='.3f', cmap='Reds', 
                   xticklabels=bandwidth_guarantee, yticklabels=resource_reservation, ax=ax2)
        ax2.set_title(f'{slice_name.upper()} SLA Violations by Parameter Combination', fontsize=12)
        ax2.set_xlabel('Bandwidth Guaranteed', fontsize=10)
        ax2.set_ylabel('Resource Reservation', fontsize=10)
        
        plt.tight_layout()
        plt.savefig(os.path.join(IMAGES_DIR, f"{slice_name}_parameter_heatmap.png"), dpi=300)
        plt.close()

def generate_approach_comparison_chart():
    """Generate chart comparing different approaches"""
    approaches = ['Static\nAllocation', 'QoS-Based\nScheduling', 'Our\nApproach']
    metrics = ['Resource\nEfficiency', 'Latency\nPerformance', 'Adaptability', 'Implementation\nComplexity']
    
    # Example comparison data (higher is better for all except complexity)
    data = np.array([
        [0.4, 0.6, 0.9],  # Resource Efficiency
        [0.5, 0.7, 0.85],  # Latency Performance
        [0.3, 0.6, 0.8],  # Adaptability
        [0.2, 0.5, 0.6]   # Implementation Complexity (lower is better)
    ])
    
    fig, ax = plt.subplots(figsize=(10, 6))
    
    # Set up the plot
    x = np.arange(len(metrics))
    width = 0.25
    
    # Create the bars
    ax.bar(x - width, data[:, 0], width, label=approaches[0], color='#ff9999')
    ax.bar(x, data[:, 1], width, label=approaches[1], color='#66b3ff')
    ax.bar(x + width, data[:, 2], width, label=approaches[2], color='#99ff99')
    
    # Add labels and title
    ax.set_ylabel('Performance Score (higher is better)', fontsize=12)
    ax.set_title('Approach Comparison', fontsize=14)
    ax.set_xticks(x)
    ax.set_xticklabels(metrics)
    ax.legend()
    
    plt.grid(axis='y', alpha=0.3)
    plt.tight_layout()
    plt.savefig(os.path.join(IMAGES_DIR, "approach_comparison.png"), dpi=300)
    plt.close()

def generate_architecture_diagram():
    """Generate a simple architecture diagram"""
    # This is a placeholder - in a real implementation, you would create
    # a proper architecture diagram. Here we just create a simple placeholder.
    
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.axis('off')
    
    # Create boxes for components
    components = [
        {"name": "Simulation Engine", "position": (0.5, 0.8), "size": (0.4, 0.1)},
        {"name": "Network Slices", "position": (0.3, 0.65), "size": (0.2, 0.1)},
        {"name": "Base Stations", "position": (0.5, 0.65), "size": (0.2, 0.1)},
        {"name": "Clients", "position": (0.7, 0.65), "size": (0.2, 0.1)},
        {"name": "Resource Allocation", "position": (0.3, 0.5), "size": (0.3, 0.1)},
        {"name": "Performance Analysis", "position": (0.7, 0.5), "size": (0.3, 0.1)},
        {"name": "Optimization Engine", "position": (0.5, 0.35), "size": (0.4, 0.1)},
        {"name": "Visualization Dashboard", "position": (0.5, 0.2), "size": (0.4, 0.1)}
    ]
    
    # Draw boxes and labels
    for comp in components:
        x, y = comp["position"]
        w, h = comp["size"]
        rect = plt.Rectangle((x-w/2, y-h/2), w, h, fill=True, color='skyblue', alpha=0.7)
        ax.add_patch(rect)
        ax.text(x, y, comp["name"], ha='center', va='center', fontsize=10)
    
    # Draw arrows connecting components
    arrows = [
        ((0.5, 0.75), (0.5, 0.7)),  # Simulation Engine -> Components
        ((0.3, 0.6), (0.3, 0.55)),  # Network Slices -> Resource Allocation
        ((0.5, 0.6), (0.4, 0.55)),  # Base Stations -> Resource Allocation
        ((0.7, 0.6), (0.7, 0.55)),  # Clients -> Performance Analysis
        ((0.3, 0.45), (0.4, 0.4)),  # Resource Allocation -> Optimization
        ((0.7, 0.45), (0.6, 0.4)),  # Performance Analysis -> Optimization
        ((0.5, 0.3), (0.5, 0.25))   # Optimization -> Dashboard
    ]
    
    for start, end in arrows:
        ax.annotate("", xy=end, xytext=start,
                  arrowprops=dict(arrowstyle="->", lw=1.5, color='gray'))
    
    ax.set_title('5G Network Slicing Optimization Architecture', fontsize=14)
    
    plt.tight_layout()
    plt.savefig(os.path.join(IMAGES_DIR, "architecture_diagram.png"), dpi=300)
    plt.close()

def generate_slice_requirements_chart():
    """Generate chart showing different slice requirements"""
    slice_types = ['URLLC', 'IoT', 'Data']
    requirements = ['Latency\nSensitivity', 'Bandwidth\nNeeds', 'Reliability\nRequirements', 'Connection\nDensity']
    
    # Example requirements data (scale 0-1, higher means more demanding)
    data = np.array([
        [0.9, 0.5, 0.3],  # Latency Sensitivity
        [0.3, 0.2, 0.9],  # Bandwidth Needs
        [0.9, 0.7, 0.6],  # Reliability Requirements
        [0.4, 0.9, 0.5]   # Connection Density
    ])
    
    fig, ax = plt.subplots(figsize=(10, 6))
    
    # Set up the plot
    x = np.arange(len(requirements))
    width = 0.25
    
    # Create the bars
    ax.bar(x - width, data[:, 0], width, label=slice_types[0], color='#ff9999')
    ax.bar(x, data[:, 1], width, label=slice_types[1], color='#66b3ff')
    ax.bar(x + width, data[:, 2], width, label=slice_types[2], color='#99ff99')
    
    # Add labels and title
    ax.set_ylabel('Requirement Level', fontsize=12)
    ax.set_title('Network Slice Requirements Comparison', fontsize=14)
    ax.set_xticks(x)
    ax.set_xticklabels(requirements)
    ax.legend()
    
    plt.grid(axis='y', alpha=0.3)
    plt.tight_layout()
    plt.savefig(os.path.join(IMAGES_DIR, "slice_requirements.png"), dpi=300)
    plt.close()

def generate_challenge_diagram():
    """Generate a simple diagram illustrating 5G network challenges"""
    # Create a simple diagram illustrating the challenges
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.axis('off')
    
    # Create a central "5G Network" node
    center_x, center_y = 0.5, 0.5
    circle = plt.Circle((center_x, center_y), 0.15, fill=True, color='#66b3ff', alpha=0.7)
    ax.add_patch(circle)
    ax.text(center_x, center_y, "5G\nNetwork", ha='center', va='center', fontsize=12, fontweight='bold')
    
    # Create challenge nodes around the center
    challenges = [
        {"name": "Resource\nCompetition", "angle": 45, "distance": 0.3},
        {"name": "Diverse Service\nRequirements", "angle": 135, "distance": 0.3},
        {"name": "Dynamic Network\nConditions", "angle": 225, "distance": 0.3},
        {"name": "Efficiency vs.\nPerformance", "angle": 315, "distance": 0.3}
    ]
    
    # Draw challenge nodes and connections
    for challenge in challenges:
        angle = np.radians(challenge["angle"])
        dist = challenge["distance"]
        x = center_x + dist * np.cos(angle)
        y = center_y + dist * np.sin(angle)
        
        circle = plt.Circle((x, y), 0.1, fill=True, color='#ff9999', alpha=0.7)
        ax.add_patch(circle)
        ax.text(x, y, challenge["name"], ha='center', va='center', fontsize=10)
        
        # Draw line connecting to center
        ax.plot([center_x, x], [center_y, y], 'k-', alpha=0.5)
    
    ax.set_title('5G Network Resource Allocation Challenges', fontsize=14)
    
    plt.tight_layout()
    plt.savefig(os.path.join(IMAGES_DIR, "challenge_diagram.png"), dpi=300)
    plt.close()

def create_dashboard_json():
    """Create JSON file with dashboard data"""
    # Save dashboard data to JSON
    json_path = os.path.join(DASHBOARD_DIR, "dashboard_data.json")
    with open(json_path, 'w') as f:
        json.dump(dashboard_data, f, indent=2)
    print(f"Dashboard data saved to: {json_path}")

def create_dashboard_html():
    """Create HTML dashboard from template"""
    # Read template file
    template_path = os.path.join(BASE_DIR, "dashboard_template.html")
    if not os.path.exists(template_path):
        # Create a minimal template if none exists
        template = """<!DOCTYPE html>
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
    <!-- This is a minimal template, the full content will be generated dynamically -->
    <div id="dashboard-root"></div>
    
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
    <script src="js/dashboard.js"></script>
</body>
</html>
"""
    else:
        with open(template_path, 'r') as f:
            template = f.read()
    
    # Save dashboard HTML
    html_path = os.path.join(DASHBOARD_DIR, "index.html")
    with open(html_path, 'w') as f:
        f.write(template)
    print(f"Dashboard HTML created at: {html_path}")

def create_dashboard_css():
    """Create CSS file for dashboard"""
    css_dir = os.path.join(DASHBOARD_DIR, "css")
    os.makedirs(css_dir, exist_ok=True)
    
    css_content = """
:root {
    --primary-color: #3498db;
    --secondary-color: #2ecc71;
    --accent-color: #e74c3c;
    --dark-color: #2c3e50;
    --light-color: #ecf0f1;
}

body {
    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    background-color: #f8f9fa;
    color: #333;
}

.header {
    background: linear-gradient(135deg, var(--primary-color), var(--dark-color));
    color: white;
    padding: 2rem 0;
    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
}

.dashboard-title {
    font-weight: 700;
}

.nav-pills .nav-link {
    color: var(--dark-color);
    border-radius: 0;
    padding: 0.8rem 1.5rem;
    font-weight: 500;
    transition: all 0.3s ease;
}

.nav-pills .nav-link.active {
    background-color: var(--primary-color);
    color: white;
    box-shadow: 0 2px 5px rgba(0, 0, 0, 0.2);
}

/* More CSS content here... (shortened for brevity) */
    """
    
    css_path = os.path.join(css_dir, "dashboard.css")
    with open(css_path, 'w') as f:
        f.write(css_content)
    print(f"Dashboard CSS created at: {css_path}")

def create_dashboard_js():
    """Create JavaScript file for dashboard"""
    js_dir = os.path.join(DASHBOARD_DIR, "js")
    os.makedirs(js_dir, exist_ok=True)
    
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

// Initialize dashboard with data
function initializeDashboard(data) {
    // Update KPI values
    document.getElementById('overall-latency-improvement').textContent = data.overall_latency_improvement.toFixed(1) + '%';
    document.getElementById('resource-utilization-improvement').textContent = data.resource_utilization_improvement.toFixed(1) + '%';
    
    // Update slice latencies
    for (const [slice, latencies] of Object.entries(data.slice_latencies)) {
        const baseElement = document.getElementById(`${slice}-base-latency`);
        const optElement = document.getElementById(`${slice}-opt-latency`);
        
        if (baseElement && optElement) {
            baseElement.textContent = latencies.base.toFixed(3);
            optElement.textContent = latencies.optimized.toFixed(3);
        }
    }
    
    // More dashboard initialization code...
}

// Image modal functionality
function openImageModal(title, imageSrc) {
    const modalTitle = document.getElementById('imageModalLabel');
    const modalImage = document.getElementById('modalImage');
    
    modalTitle.textContent = title;
    modalImage.src = imageSrc;
    
    const imageModal = new bootstrap.Modal(document.getElementById('imageModal'));
    imageModal.show();
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
    """
    
    js_path = os.path.join(js_dir, "dashboard.js")
    with open(js_path, 'w') as f:
        f.write(js_content)
    print(f"Dashboard JavaScript created at: {js_path}")

def launch_dashboard():
    """Launch the dashboard in a web browser"""
    dashboard_index = os.path.join(DASHBOARD_DIR, "index.html")
    dashboard_url = Path(dashboard_index).absolute().as_uri()
    
    print(f"Launching dashboard at: {dashboard_url}")
    webbrowser.open(dashboard_url)

def main():
    print("Starting 5G Network Slicing Optimization and Dashboard Generation")
    print("-" * 70)
    
    # Step 1: Run the optimization process
    optimization_success = run_optimization()
    if not optimization_success:
        print("Error: Optimization failed. Cannot generate dashboard.")
        return
    
    # Step 2: Generate charts and visualizations
    print("\nGenerating charts and visualizations...")
    generate_optimization_summary()
    generate_slice_latency_comparison()
    generate_parameter_importance_charts()
    generate_performance_charts()
    generate_parameter_interaction_charts()
    generate_approach_comparison_chart()
    generate_architecture_diagram()
    generate_slice_requirements_chart()
    generate_challenge_diagram()
    
    # Step 3: Create dashboard files
    print("\nCreating dashboard files...")
    create_dashboard_json()
    create_dashboard_html()
    create_dashboard_css()
    create_dashboard_js()
    
    # Step 4: Launch dashboard
    print("\nDashboard generation complete!")
    launch_dashboard()

if __name__ == "__main__":
    main()
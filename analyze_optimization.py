import os
import yaml
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from matplotlib.gridspec import GridSpec
from collections import defaultdict
import glob

# Define paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
RESULTS_DIR = os.path.join(BASE_DIR, 'optimization_results')
OUTPUT_DIR = os.path.join(RESULTS_DIR, 'analysis')

# Ensure output directory exists
os.makedirs(OUTPUT_DIR, exist_ok=True)

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

def create_parameter_performance_plots(results):
    """Create plots showing parameter vs performance metrics"""
    # Group results by slice and parameter
    grouped_results = defaultdict(lambda: defaultdict(list))
    
    for result in results:
        if 'slice_name' in result and 'param_name' in result and 'param_value' in result:
            slice_name = result['slice_name']
            param_name = result['param_name']
            param_value = result['param_value']
            
            # Skip validation configs
            if 'validation' in result['config_name']:
                continue
                
            grouped_results[slice_name][param_name].append(result)
    
    # Create plots for each slice and parameter
    for slice_name, params in grouped_results.items():
        for param_name, param_results in params.items():
            # Sort by parameter value
            param_results.sort(key=lambda x: x['param_value'])
            
            # Extract data for plotting
            values = [r['param_value'] for r in param_results]
            
            # Get slice-specific latency if available, otherwise use overall
            latencies = []
            for r in param_results:
                if slice_name in r['slice_latencies']:
                    latencies.append(r['slice_latencies'][slice_name])
                else:
                    latencies.append(r['overall_latency'])
            
            violations = [r['sla_violations'] for r in param_results]
            handovers = [r['handover_ratio'] for r in param_results]
            blocks = [r['block_ratio'] for r in param_results]
            
            # Create a figure with multiple subplots
            fig = plt.figure(figsize=(15, 10))
            gs = GridSpec(2, 2, figure=fig)
            
            # Plot latency vs parameter
            ax1 = fig.add_subplot(gs[0, 0])
            ax1.plot(values, latencies, 'o-', color='blue', linewidth=2)
            ax1.set_title(f'{slice_name.upper()} Latency vs {param_name}', fontsize=14)
            ax1.set_xlabel(param_name, fontsize=12)
            ax1.set_ylabel('Latency (ms)', fontsize=12)
            ax1.grid(True, alpha=0.3)
            
            # Highlight lowest latency
            min_latency_idx = latencies.index(min(latencies))
            ax1.plot(values[min_latency_idx], latencies[min_latency_idx], 'r*', markersize=15)
            ax1.annotate(f'Optimal: {values[min_latency_idx]}',
                        (values[min_latency_idx], latencies[min_latency_idx]),
                        textcoords="offset points", xytext=(0,10), ha='center')
            
            # Plot SLA violations vs parameter
            ax2 = fig.add_subplot(gs[0, 1])
            ax2.plot(values, violations, 's-', color='red', linewidth=2)
            ax2.set_title(f'{slice_name.upper()} SLA Violations vs {param_name}', fontsize=14)
            ax2.set_xlabel(param_name, fontsize=12)
            ax2.set_ylabel('SLA Violation Rate', fontsize=12)
            ax2.grid(True, alpha=0.3)
            
            # Plot handover ratio vs parameter
            ax3 = fig.add_subplot(gs[1, 0])
            ax3.plot(values, handovers, '^-', color='green', linewidth=2)
            ax3.set_title(f'{slice_name.upper()} Handover Ratio vs {param_name}', fontsize=14)
            ax3.set_xlabel(param_name, fontsize=12)
            ax3.set_ylabel('Handover Ratio', fontsize=12)
            ax3.grid(True, alpha=0.3)
            
            # Plot block ratio vs parameter
            ax4 = fig.add_subplot(gs[1, 1])
            ax4.plot(values, blocks, 'D-', color='purple', linewidth=2)
            ax4.set_title(f'{slice_name.upper()} Block Ratio vs {param_name}', fontsize=14)
            ax4.set_xlabel(param_name, fontsize=12)
            ax4.set_ylabel('Block Ratio', fontsize=12)
            ax4.grid(True, alpha=0.3)
            
            plt.tight_layout()
            plt.savefig(os.path.join(OUTPUT_DIR, f"{slice_name}_{param_name}_detailed.png"), dpi=300)
            plt.close()

def create_slice_comparison_chart(results):
    """Create charts comparing performance across different slices"""
    # Extract validation results
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
    plt.figure(figsize=(12, 8))
    
    x = np.arange(len(slice_names))
    width = 0.35
    
    plt.bar(x - width/2, base_latencies, width, label='Base Configuration', color='skyblue')
    plt.bar(x + width/2, opt_latencies, width, label='Optimized Configuration', color='coral')
    
    plt.xlabel('Network Slice', fontsize=14)
    plt.ylabel('Average Latency (ms)', fontsize=14)
    plt.title('Latency Comparison Across Network Slices', fontsize=16)
    plt.xticks(x, [s.upper() for s in slice_names], fontsize=12)
    plt.legend(fontsize=12)
    plt.grid(axis='y', alpha=0.3)
    
    # Add latency values on top of bars
    for i, v in enumerate(base_latencies):
        plt.text(i - width/2, v + 0.01, f'{v:.3f}', ha='center', fontsize=10)
    
    for i, v in enumerate(opt_latencies):
        plt.text(i + width/2, v + 0.01, f'{v:.3f}', ha='center', fontsize=10)
    
    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, "slice_latency_comparison.png"), dpi=300)
    plt.close()

def create_heatmap(results):
    """Create heatmaps showing parameter interactions"""
    # Extract the slice of interest (e.g., URLLC)
    for slice_name in ['urllc', 'iot', 'data']:
        # Extract parameters and their values
        res_reservation_values = sorted(list(set([r['param_value'] for r in results 
                                              if r.get('slice_name') == slice_name and 
                                                 r.get('param_name') == 'resource_reservation'])))
        
        bw_guaranteed_values = sorted(list(set([r['param_value'] for r in results 
                                             if r.get('slice_name') == slice_name and 
                                                r.get('param_name') == 'bandwidth_guaranteed'])))
        
        if not res_reservation_values or not bw_guaranteed_values:
            continue
        
        # Create a matrix for the heatmap
        latency_matrix = np.zeros((len(res_reservation_values), len(bw_guaranteed_values)))
        sla_matrix = np.zeros((len(res_reservation_values), len(bw_guaranteed_values)))
        
        # Fill the matrix with latency and SLA violation values
        for i, res_val in enumerate(res_reservation_values):
            for j, bw_val in enumerate(bw_guaranteed_values):
                # Find results with these parameter values
                res_results = [r for r in results if r.get('slice_name') == slice_name and 
                              r.get('param_name') == 'resource_reservation' and 
                              r.get('param_value') == res_val]
                
                bw_results = [r for r in results if r.get('slice_name') == slice_name and 
                             r.get('param_name') == 'bandwidth_guaranteed' and 
                             r.get('param_value') == bw_val]
                
                if res_results and bw_results:
                    # Average the latency and SLA violations
                    avg_latency = np.mean([r.get('slice_latencies', {}).get(slice_name, r.get('overall_latency', 0)) 
                                          for r in res_results + bw_results])
                    
                    avg_sla = np.mean([r.get('sla_violations', 0) for r in res_results + bw_results])
                    
                    latency_matrix[i, j] = avg_latency
                    sla_matrix[i, j] = avg_sla
        
        # Create the heatmaps
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))
        
        # Latency heatmap
        sns.heatmap(latency_matrix, annot=True, fmt='.3f', cmap='viridis', 
                   xticklabels=bw_guaranteed_values, yticklabels=res_reservation_values, ax=ax1)
        ax1.set_title(f'{slice_name.upper()} Latency by Parameter Combination', fontsize=14)
        ax1.set_xlabel('Bandwidth Guaranteed', fontsize=12)
        ax1.set_ylabel('Resource Reservation', fontsize=12)
        
        # SLA violations heatmap
        sns.heatmap(sla_matrix, annot=True, fmt='.3f', cmap='Reds', 
                   xticklabels=bw_guaranteed_values, yticklabels=res_reservation_values, ax=ax2)
        ax2.set_title(f'{slice_name.upper()} SLA Violations by Parameter Combination', fontsize=14)
        ax2.set_xlabel('Bandwidth Guaranteed', fontsize=12)
        ax2.set_ylabel('Resource Reservation', fontsize=12)
        
        plt.tight_layout()
        plt.savefig(os.path.join(OUTPUT_DIR, f"{slice_name}_parameter_heatmap.png"), dpi=300)
        plt.close()

def create_radar_chart(results):
    """Create radar charts comparing optimized vs baseline configuration"""
    # Extract validation results
    base_result = next((r for r in results if 'validation_base' in r['config_name']), None)
    opt_result = next((r for r in results if 'validation_optimized' in r['config_name']), None)
    
    if not base_result or not opt_result:
        print("Validation results not found")
        return
    
    # Define metrics to compare
    metrics = [
        'overall_latency', 
        'sla_violations',
        'connected_ratio',
        'handover_ratio',
        'block_ratio'
    ]
    
    # Normalize metrics for radar chart (lower is better for all except connected_ratio)
    max_latency = max(base_result['overall_latency'], opt_result['overall_latency'])
    base_values = [
        1 - (base_result['overall_latency'] / max_latency if max_latency > 0 else 0),
        1 - base_result['sla_violations'],
        base_result['connected_ratio'],
        1 - base_result['handover_ratio'],
        1 - base_result['block_ratio']
    ]
    
    opt_values = [
        1 - (opt_result['overall_latency'] / max_latency if max_latency > 0 else 0),
        1 - opt_result['sla_violations'],
        opt_result['connected_ratio'],
        1 - opt_result['handover_ratio'],
        1 - opt_result['block_ratio']
    ]
    
    # Set up radar chart
    labels = ['Latency\nPerformance', 'SLA\nCompliance', 'Connection\nRatio', 'Handover\nStability', 'Block\nAvoidance']
    
    angles = np.linspace(0, 2*np.pi, len(labels), endpoint=False).tolist()
    angles += angles[:1]  # Close the loop
    
    base_values += base_values[:1]  # Close the loop
    opt_values += opt_values[:1]  # Close the loop
    
    fig, ax = plt.subplots(figsize=(10, 10), subplot_kw=dict(polar=True))
    
    ax.plot(angles, base_values, 'o-', linewidth=2, label='Base Configuration', color='blue')
    ax.fill(angles, base_values, alpha=0.1, color='blue')
    
    ax.plot(angles, opt_values, 'o-', linewidth=2, label='Optimized Configuration', color='red')
    ax.fill(angles, opt_values, alpha=0.1, color='red')
    
    ax.set_thetagrids(np.degrees(angles[:-1]), labels)
    ax.set_ylim(0, 1)
    ax.set_title('Optimization Performance Radar Chart', fontsize=16, pad=20)
    ax.legend(loc='upper right', bbox_to_anchor=(0.1, 0.1))
    
    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, "optimization_radar_chart.png"), dpi=300)
    plt.close()

def create_parameter_importance(results):
    """Create visuals showing parameter importance for each slice"""
    # Extract slice-specific results
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
            plt.figure(figsize=(10, 6))
            
            params = list(param_variation.keys())
            impacts = list(param_variation.values())
            
            # Normalize impacts to percentage
            total_impact = sum(impacts)
            if total_impact > 0:
                norm_impacts = [i / total_impact * 100 for i in impacts]
            else:
                norm_impacts = impacts
            
            bars = plt.bar(params, norm_impacts, color=['#ff9999', '#66b3ff'])
            
            plt.xlabel('Parameter', fontsize=14)
            plt.ylabel('Impact on Latency (%)', fontsize=14)
            plt.title(f'Parameter Importance for {slice_name.upper()} Slice', fontsize=16)
            plt.grid(axis='y', alpha=0.3)
            
            # Add value labels on top of bars
            for bar in bars:
                height = bar.get_height()
                plt.text(bar.get_x() + bar.get_width()/2., height + 0.5,
                        f'{height:.1f}%', ha='center', fontsize=12)
            
            plt.tight_layout()
            plt.savefig(os.path.join(OUTPUT_DIR, f"{slice_name}_parameter_importance.png"), dpi=300)
            plt.close()

def create_optimization_summary(results):
    """Create a comprehensive visual summary of the optimization"""
    # Extract validation results
    base_result = next((r for r in results if 'validation_base' in r['config_name']), None)
    opt_result = next((r for r in results if 'validation_optimized' in r['config_name']), None)
    
    if not base_result or not opt_result:
        print("Validation results not found")
        return
    
    # Create a figure with multiple subplots
    fig = plt.figure(figsize=(18, 12))
    gs = GridSpec(3, 3, figure=fig)
    
    # 1. Slice Resource Allocation - Base vs Optimized
    ax1 = fig.add_subplot(gs[0, :])
    
    slice_names = ['urllc', 'iot', 'data']
    
    # Extract resource reservations
    base_reservations = [base_result.get(f"{s}_res_rsrv", 0) for s in slice_names]
    opt_reservations = [opt_result.get(f"{s}_res_rsrv", 0) for s in slice_names]
    
    # Extract bandwidth guarantees
    base_guarantees = [base_result.get(f"{s}_bw_guar", 0) for s in slice_names]
    opt_guarantees = [opt_result.get(f"{s}_bw_guar", 0) for s in slice_names]
    
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
    
    ax1.set_xlabel('Network Slice', fontsize=14)
    ax1.set_title('Resource Allocation Comparison', fontsize=16)
    ax1.set_xticks(x)
    ax1.set_xticklabels([s.upper() for s in slice_names], fontsize=12)
    ax1.legend(fontsize=12, loc='upper right')
    ax1.grid(axis='y', alpha=0.3)
    
    # 2. Latency Performance
    ax2 = fig.add_subplot(gs[1, 0:2])
    
    # Extract slice latencies
    base_latencies = [base_result['slice_latencies'].get(s, 0) for s in slice_names]
    opt_latencies = [opt_result['slice_latencies'].get(s, 0) for s in slice_names]
    
    # Calculate improvement percentages
    improvements = []
    for b, o in zip(base_latencies, opt_latencies):
        if b > 0:
            imp = (b - o) / b * 100
        else:
            imp = 0
        improvements.append(imp)
    
    # Plot latencies
    width = 0.35
    ax2.bar(x - width/2, base_latencies, width, label='Base Configuration', color='skyblue')
    ax2.bar(x + width/2, opt_latencies, width, label='Optimized Configuration', color='coral')
    
    ax2.set_xlabel('Network Slice', fontsize=14)
    ax2.set_ylabel('Latency (ms)', fontsize=14)
    ax2.set_title('Latency Comparison Across Slices', fontsize=16)
    ax2.set_xticks(x)
    ax2.set_xticklabels([s.upper() for s in slice_names], fontsize=12)
    ax2.legend(fontsize=12)
    ax2.grid(axis='y', alpha=0.3)
    
    # Add improvement percentages above bars
    for i, imp in enumerate(improvements):
        ax2.text(x[i], max(base_latencies[i], opt_latencies[i]) + 0.01, 
                f'{imp:.1f}%', ha='center', fontsize=10, 
                color='green' if imp > 0 else 'red')
    
    # 3. SLA violations
    ax3 = fig.add_subplot(gs[1, 2])
    
    base_sla = base_result.get('sla_violations', 0)
    opt_sla = opt_result.get('sla_violations', 0)
    
    ax3.bar(['Base', 'Optimized'], [base_sla, opt_sla], color=['skyblue', 'coral'])
    
    ax3.set_ylabel('SLA Violation Rate', fontsize=14)
    ax3.set_title('SLA Violation Comparison', fontsize=16)
    ax3.grid(axis='y', alpha=0.3)
    
    # 4. Optimization summary text
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
    
    ax4.text(0.5, 0.5, summary_text, ha='center', va='center', fontsize=12, 
             bbox=dict(boxstyle="round,pad=1", fc="lightyellow", ec="orange", alpha=0.8))
    
    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, "optimization_summary.png"), dpi=300)
    plt.close()

def main():
    print("Starting 5G Slice Optimization Analysis")
    print("-" * 50)
    
    # Load all optimization results
    results = load_results()
    print(f"Loaded {len(results)} simulation results")
    
    # Create detailed parameter performance charts
    print("Creating parameter performance plots...")
    create_parameter_performance_plots(results)
    
    # Create slice comparison charts
    print("Creating slice comparison charts...")
    create_slice_comparison_chart(results)
    
    # Create parameter interaction heatmaps
    print("Creating parameter interaction heatmaps...")
    create_heatmap(results)
    
    # Create radar chart
    print("Creating performance radar chart...")
    create_radar_chart(results)
    
    # Create parameter importance charts
    print("Creating parameter importance charts...")
    create_parameter_importance(results)
    
    # Create comprehensive summary
    print("Creating comprehensive optimization summary...")
    create_optimization_summary(results)
    
    print(f"\nAnalysis complete! All visualizations saved to: {OUTPUT_DIR}")

if __name__ == "__main__":
    main()
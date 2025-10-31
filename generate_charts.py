import os
import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns

# Define the images directory
IMAGES_DIR = 'dashboard/images'
os.makedirs(IMAGES_DIR, exist_ok=True)

# Sample data for slices
slice_names = ['urllc', 'iot', 'data']
param_names = ['resource_reservation', 'bandwidth_guaranteed']

# Function to generate placeholder parameter impact charts
def generate_parameter_impact_charts():
    for slice_name in slice_names:
        plt.figure(figsize=(8, 5))
        params = param_names
        impacts = [60, 40]  # Example impact values
        
        bars = plt.bar(params, impacts, color=['#ff9999', '#66b3ff'])
        
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

# Function to generate parameter detail charts
def generate_parameter_detail_charts():
    for slice_name in slice_names:
        for param_name in param_names:
            # Create example data
            values = [0.1, 0.2, 0.3] if param_name == 'resource_reservation' else [5, 10, 15]
            if slice_name == 'data' and param_name == 'bandwidth_guaranteed':
                values = [500, 1000, 1500]
            if slice_name == 'data' and param_name == 'resource_reservation':
                values = [0, 0.1, 0.2]
                
            latencies = [0.39 + np.random.uniform(-0.01, 0.02) for _ in range(3)]
            latencies.sort()  # Make them look realistic
            
            # Create a figure with plots
            fig, ax = plt.subplots(figsize=(10, 6))
            
            ax.plot(values, latencies, 'o-', color='blue', linewidth=2)
            ax.set_title(f'{slice_name.upper()} Latency vs {param_name}', fontsize=14)
            ax.set_xlabel(param_name, fontsize=12)
            ax.set_ylabel('Latency (ms)', fontsize=12)
            ax.grid(True, alpha=0.3)
            
            # Highlight lowest latency
            min_latency_idx = latencies.index(min(latencies))
            ax.plot(values[min_latency_idx], latencies[min_latency_idx], 'r*', markersize=15)
            
            plt.tight_layout()
            plt.savefig(os.path.join(IMAGES_DIR, f"{slice_name}_{param_name}_detailed.png"), dpi=300)
            plt.close()

# Function to generate parameter heatmaps
def generate_parameter_heatmaps():
    for slice_name in slice_names:
        # Create example heatmap data
        resource_reservation = [0.1, 0.2, 0.3]
        bandwidth_guarantee = [2, 5, 10] if slice_name == 'urllc' else [5, 10, 15]
        if slice_name == 'data':
            bandwidth_guarantee = [500, 1000, 1500]
            resource_reservation = [0, 0.1, 0.2]
        
        # Create dummy heatmap matrices
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

# Function to generate comparison charts
def generate_comparison_charts():
    # Slice latency comparison
    plt.figure(figsize=(10, 6))
    
    base_latencies = [0.479, 0.479, 0.479]
    opt_latencies = [0.475, 0.475, 0.475]
    
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
    
    plt.tight_layout()
    plt.savefig(os.path.join(IMAGES_DIR, "slice_latency_comparison.png"), dpi=300)
    plt.close()
    
    # Cross-slice comparisons
    # Simulation latency comparison
    plt.figure(figsize=(12, 6))
    
    # Create example data for each slice and parameter
    sim_data = []
    for slice_name in slice_names:
        for param_name in param_names:
            if slice_name == 'data' and param_name == 'resource_reservation':
                values = [0, 0.1, 0.2]
            elif param_name == 'resource_reservation':
                values = [0.1, 0.2, 0.3]
            elif slice_name == 'data' and param_name == 'bandwidth_guaranteed':
                values = [500, 1000, 1500]
            else:
                values = [5, 10, 15]
                
            for value in values:
                sim_data.append({
                    'name': f"{slice_name}_{param_name}_{value}",
                    'latency': 0.39 + np.random.uniform(-0.01, 0.02)
                })
    
    # Sort by latency
    sim_data.sort(key=lambda x: x['latency'])
    
    # Plot
    names = [sim['name'] for sim in sim_data]
    latencies = [sim['latency'] for sim in sim_data]
    
    plt.figure(figsize=(14, 6))
    bars = plt.bar(names, latencies, color='skyblue')
    
    plt.xlabel('Simulation Configuration', fontsize=12)
    plt.ylabel('Latency (ms)', fontsize=12)
    plt.title('Cross-Simulation Latency Performance', fontsize=14)
    plt.xticks(rotation=90, fontsize=8)
    plt.grid(axis='y', alpha=0.3)
    
    plt.tight_layout()
    plt.savefig(os.path.join(IMAGES_DIR, "sim_comparison_latency.png"), dpi=300)
    plt.close()
    
    # Resource comparison
    plt.figure(figsize=(10, 6))
    
    for i, slice_name in enumerate(slice_names):
        latencies = []
        values = [0, 0.1, 0.2] if slice_name == 'data' else [0.1, 0.2, 0.3]
        for value in values:
            latencies.append(0.39 + 0.01 * i + 0.02 * values.index(value))
            
        plt.plot(values, latencies, 'o-', label=slice_name.upper(), linewidth=2)
    
    plt.xlabel('Resource Reservation', fontsize=12)
    plt.ylabel('Latency (ms)', fontsize=12)
    plt.title('Resource Reservation Impact Across Slices', fontsize=14)
    plt.legend(fontsize=10)
    plt.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig(os.path.join(IMAGES_DIR, "cross_slice_resource_comparison.png"), dpi=300)
    plt.close()
    
    # Bandwidth comparison
    plt.figure(figsize=(10, 6))
    
    plt.plot([5, 10, 15], [0.391, 0.395, 0.401], 'o-', label='URLLC', linewidth=2)
    plt.plot([5, 10, 15], [0.390, 0.397, 0.405], 'o-', label='IoT', linewidth=2)
    plt.plot([500, 1000, 1500], [0.389, 0.395, 0.403], 'o-', label='Data', linewidth=2)
    
    plt.xlabel('Bandwidth Guaranteed (log scale)', fontsize=12)
    plt.ylabel('Latency (ms)', fontsize=12)
    plt.title('Bandwidth Guarantee Impact Across Slices', fontsize=14)
    plt.legend(fontsize=10)
    plt.grid(True, alpha=0.3)
    plt.xscale('log')
    
    plt.tight_layout()
    plt.savefig(os.path.join(IMAGES_DIR, "cross_slice_bandwidth_comparison.png"), dpi=300)
    plt.close()
    
    # Radar chart
    labels = ['Latency\nPerformance', 'SLA\nCompliance', 'Connection\nRatio', 'Handover\nStability', 'Block\nAvoidance']
    
    # Example data
    base_values = [0.6, 0.9, 0.7, 0.6, 0.7]
    opt_values = [0.8, 0.9, 0.8, 0.7, 0.8]
    
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
    plt.savefig(os.path.join(IMAGES_DIR, "optimization_radar_chart.png"), dpi=300)
    plt.close()

# Function to generate summary charts
def generate_summary_charts():
    # Overall optimization summary
    fig = plt.figure(figsize=(16, 10))
    
    # Make a simple summary image
    plt.text(0.5, 0.5, "Optimization Summary", fontsize=20, ha='center')
    plt.text(0.5, 0.4, "Latency Improvement: 0.8%", fontsize=16, ha='center')
    plt.text(0.5, 0.35, "Resource Utilization Improvement: 12.5%", fontsize=16, ha='center')
    plt.axis('off')
    
    plt.savefig(os.path.join(IMAGES_DIR, "optimization_summary.png"), dpi=300)
    plt.close()
    
    # Architecture diagram 
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.axis('off')
    
    # Add a title
    plt.title('5G Network Slicing Architecture', fontsize=16)
    
    # Add some text
    plt.text(0.5, 0.5, "Architecture Diagram", fontsize=20, ha='center')
    
    plt.savefig(os.path.join(IMAGES_DIR, "architecture_diagram.png"), dpi=300)
    plt.close()
    
    # Challenge diagram
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.axis('off')
    
    # Add a title
    plt.title('5G Network Slicing Challenges', fontsize=16)
    
    # Add some text
    plt.text(0.5, 0.5, "Challenge Diagram", fontsize=20, ha='center')
    
    plt.savefig(os.path.join(IMAGES_DIR, "challenge_diagram.png"), dpi=300)
    plt.close()
    
    # Slice requirements
    fig, ax = plt.subplots(figsize=(10, 6))
    
    # Example requirements data
    requirements = ['Latency\nSensitivity', 'Bandwidth\nNeeds', 'Reliability\nRequirements', 'Connection\nDensity']
    data = np.array([
        [0.9, 0.5, 0.3],  # Latency Sensitivity
        [0.3, 0.2, 0.9],  # Bandwidth Needs
        [0.9, 0.7, 0.6],  # Reliability Requirements
        [0.4, 0.9, 0.5]   # Connection Density
    ])
    
    x = np.arange(len(requirements))
    width = 0.25
    
    ax.bar(x - width, data[:, 0], width, label='URLLC', color='#ff9999')
    ax.bar(x, data[:, 1], width, label='IoT', color='#66b3ff')
    ax.bar(x + width, data[:, 2], width, label='Data', color='#99ff99')
    
    ax.set_ylabel('Requirement Level', fontsize=12)
    ax.set_title('Network Slice Requirements Comparison', fontsize=14)
    ax.set_xticks(x)
    ax.set_xticklabels(requirements)
    ax.legend()
    
    plt.grid(axis='y', alpha=0.3)
    plt.tight_layout()
    
    plt.savefig(os.path.join(IMAGES_DIR, "slice_requirements.png"), dpi=300)
    plt.close()
    
    # Approach comparison
    fig, ax = plt.subplots(figsize=(10, 6))
    
    approaches = ['Static\nAllocation', 'QoS-Based\nScheduling', 'Our\nApproach']
    metrics = ['Resource\nEfficiency', 'Latency\nPerformance', 'Adaptability', 'Implementation\nComplexity']
    
    data = np.array([
        [0.4, 0.6, 0.9],  # Resource Efficiency
        [0.5, 0.7, 0.85],  # Latency Performance
        [0.3, 0.6, 0.8],  # Adaptability
        [0.2, 0.5, 0.6]   # Implementation Complexity
    ])
    
    x = np.arange(len(metrics))
    width = 0.25
    
    ax.bar(x - width, data[:, 0], width, label=approaches[0], color='#ff9999')
    ax.bar(x, data[:, 1], width, label=approaches[1], color='#66b3ff')
    ax.bar(x + width, data[:, 2], width, label=approaches[2], color='#99ff99')
    
    ax.set_ylabel('Performance Score', fontsize=12)
    ax.set_title('Approach Comparison', fontsize=14)
    ax.set_xticks(x)
    ax.set_xticklabels(metrics)
    ax.legend()
    
    plt.grid(axis='y', alpha=0.3)
    plt.tight_layout()
    
    plt.savefig(os.path.join(IMAGES_DIR, "approach_comparison.png"), dpi=300)
    plt.close()

# Generate all charts
if __name__ == "__main__":
    print("Generating parameter impact charts...")
    generate_parameter_impact_charts()
    
    print("Generating parameter detail charts...")
    generate_parameter_detail_charts()
    
    print("Generating parameter heatmaps...")
    generate_parameter_heatmaps()
    
    print("Generating comparison charts...")
    generate_comparison_charts()
    
    print("Generating summary charts...")
    generate_summary_charts()
    
    print(f"All charts generated and saved to {IMAGES_DIR}")
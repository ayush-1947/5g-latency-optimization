import os
import sys
import yaml
import copy
import subprocess
import time
import matplotlib.pyplot as plt
from collections import defaultdict

# Define paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_DIR = os.path.join(BASE_DIR, 'optimization_results')

# Ensure output directory exists
os.makedirs(OUTPUT_DIR, exist_ok=True)

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
    
    raise FileNotFoundError(f"Could not find example-input.yml")

def save_config(config, filename):
    """Save a configuration to a file"""
    path = os.path.join(OUTPUT_DIR, filename)
    with open(path, 'w') as f:
        yaml.dump(config, f)
    return path

def run_simulation(config_path, output_prefix):
    """Run the simulation with a given configuration"""
    log_file = os.path.join(OUTPUT_DIR, f"{output_prefix}_output.txt")
    plot_file = os.path.join(OUTPUT_DIR, f"{output_prefix}_plot.png")
    
    # Make a copy of the config with updated output paths
    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)
    
    config['settings']['logging'] = True
    config['settings']['log_file'] = log_file
    config['settings']['plotting_params']['plot_file'] = plot_file
    config['settings']['plotting_params']['plot_save'] = True
    config['settings']['plotting_params']['plot_show'] = False
    
    # Save the modified config
    modified_config_path = os.path.join(OUTPUT_DIR, f"{output_prefix}_modified.yml")
    with open(modified_config_path, 'w') as f:
        yaml.dump(config, f)
    
    # Run the simulation
    print(f"Running simulation with config: {output_prefix}")
    result = subprocess.run(['python', '-m', 'slicemaster', modified_config_path], 
                            stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    
    # Check for errors
    if result.returncode != 0:
        print(f"Error running simulation: {result.stderr.decode('utf-8')}")
    else:
        print(f"Simulation completed successfully")
    
    # Return the path to the log file
    return log_file

def parse_simulation_results(log_file):
    """Parse simulation results from the log file"""
    results = {
        'overall_latency': 0,
        'slice_latencies': {},
        'sla_violations': 0,
        'throughput': 0
    }
    
    try:
        with open(log_file, 'r') as f:
            content = f.read()
        
        # Extract key metrics from log
        lines = content.split('\n')
        for i, line in enumerate(lines):
            if line.strip() == "LATENCY ANALYSIS":
                # Found the latency analysis section
                for j in range(i+1, min(i+20, len(lines))):
                    if "Overall average latency:" in lines[j]:
                        try:
                            results['overall_latency'] = float(lines[j].split(":")[-1].strip())
                        except:
                            pass
                    
                    if "Average latency by slice:" in lines[j]:
                        # Read the next few lines for slice latencies
                        k = j + 1
                        while k < len(lines) and lines[k].strip().startswith("  "):
                            parts = lines[k].strip().split(":")
                            if len(parts) == 2:
                                slice_name = parts[0].strip()
                                try:
                                    slice_latency = float(parts[1].strip())
                                    results['slice_latencies'][slice_name] = slice_latency
                                except:
                                    pass
                            k += 1
                    
                    if "SLA violation rate:" in lines[j]:
                        try:
                            results['sla_violations'] = float(lines[j].split(":")[-1].strip())
                        except:
                            pass
            
            # Look for throughput information
            if "Average bandwidth usage" in line and i+1 < len(lines):
                try:
                    # This is a simplification - would need adjustment based on actual format
                    throughput_text = lines[i+1].strip()
                    if 'bps' in throughput_text.lower():
                        # Very simple parsing - would need to be adapted
                        value = float(throughput_text.split()[0])
                        unit = throughput_text.split()[1].lower()
                        
                        # Convert to a numeric value
                        if 'kbps' in unit:
                            results['throughput'] = value * 1000
                        elif 'mbps' in unit:
                            results['throughput'] = value * 1000000
                        elif 'gbps' in unit:
                            results['throughput'] = value * 1000000000
                        else:
                            results['throughput'] = value
                except:
                    pass
    
    except Exception as e:
        print(f"Error parsing results: {e}")
    
    return results

def generate_test_configs(base_config):
    """Generate test configurations for parameter sweep"""
    configs = []
    config_info = []
    
    # Define parameters to test for each slice
    param_space = {
        'urllc': {
            'resource_reservation': [0.1, 0.2, 0.3],  # Test 3 values for faster testing
            'bandwidth_guaranteed': [2, 5, 10]
        },
        'iot': {
            'resource_reservation': [0.05, 0.1, 0.15],
            'bandwidth_guaranteed': [5, 10, 15]
        },
        'data': {
            'resource_reservation': [0.0, 0.05, 0.1],
            'bandwidth_guaranteed': [500, 1000, 1500]
        }
    }
    
    # Generate configs for each parameter combination
    for slice_name, params in param_space.items():
        for param_name, values in params.items():
            for value in values:
                # Create a copy of the base config
                test_config = copy.deepcopy(base_config)
                
                # Modify the parameter
                test_config['slices'][slice_name][param_name] = value
                
                # Make simulation shorter for testing
                test_config['settings']['simulation_time'] = 20
                
                # Generate a unique name
                config_name = f"{slice_name}_{param_name}_{str(value).replace('.', '_')}"
                
                configs.append((config_name, test_config))
                config_info.append({
                    'slice_name': slice_name,
                    'param_name': param_name,
                    'param_value': value
                })
    
    return configs, config_info

def plot_results(results, output_dir):
    """Plot the results of the parameter sweep"""
    # Organize results by slice and parameter
    organized_results = defaultdict(lambda: defaultdict(list))
    
    for result in results:
        slice_name = result['slice_name']
        param_name = result['param_name']
        param_value = result['param_value']
        overall_latency = result['overall_latency']
        slice_latency = result['slice_latencies'].get(slice_name, overall_latency)
        sla_violations = result['sla_violations']
        
        organized_results[slice_name][param_name].append({
            'value': param_value,
            'latency': slice_latency,
            'sla_violations': sla_violations
        })
    
    # Create plots for each slice and parameter
    for slice_name, params in organized_results.items():
        for param_name, param_results in params.items():
            # Sort by parameter value
            param_results.sort(key=lambda x: x['value'])
            
            # Extract data for plotting
            values = [r['value'] for r in param_results]
            latencies = [r['latency'] for r in param_results]
            violations = [r['sla_violations'] for r in param_results]
            
            # Create the plot
            plt.figure(figsize=(10, 6))
            
            # Plot latency
            plt.subplot(1, 2, 1)
            plt.plot(values, latencies, 'o-', color='blue')
            plt.title(f'{slice_name} Latency vs {param_name}')
            plt.xlabel(param_name)
            plt.ylabel('Latency (ms)')
            plt.grid(True)
            
            # Plot SLA violations
            plt.subplot(1, 2, 2)
            plt.plot(values, violations, 's-', color='red')
            plt.title(f'{slice_name} SLA Violations vs {param_name}')
            plt.xlabel(param_name)
            plt.ylabel('SLA Violation Rate')
            plt.grid(True)
            
            plt.tight_layout()
            
            # Save the plot
            plot_path = os.path.join(output_dir, f"{slice_name}_{param_name}_analysis.png")
            plt.savefig(plot_path)
            plt.close()
            
            print(f"Created plot: {plot_path}")

def find_optimal_parameters(results, base_config):
    """Find the optimal parameters for each slice"""
    # Organize results by slice and parameter
    organized_results = defaultdict(lambda: defaultdict(list))
    
    for result in results:
        slice_name = result['slice_name']
        param_name = result['param_name']
        param_value = result['param_value']
        overall_latency = result['overall_latency']
        slice_latency = result['slice_latencies'].get(slice_name, overall_latency)
        sla_violations = result['sla_violations']
        
        organized_results[slice_name][param_name].append({
            'value': param_value,
            'latency': slice_latency,
            'sla_violations': sla_violations
        })
    
    # Find optimal values for each slice and parameter
    optimal_params = {}
    
    for slice_name, params in organized_results.items():
        slice_optimal = {}
        
        # Get SLA threshold
        sla_threshold = base_config['slices'][slice_name]['delay_tolerance']
        
        for param_name, param_results in params.items():
            # Different optimization strategies based on slice type
            if slice_name == 'urllc':
                # For URLLC: prioritize meeting latency SLA
                valid_results = [r for r in param_results if r['latency'] <= sla_threshold]
                if valid_results:
                    # Choose the one with the lowest SLA violations
                    best_result = min(valid_results, key=lambda r: r['sla_violations'])
                else:
                    # If none meet the SLA, choose the one with lowest latency
                    best_result = min(param_results, key=lambda r: r['latency'])
            
            elif slice_name == 'data':
                # For data: prioritize low SLA violations
                best_result = min(param_results, key=lambda r: r['sla_violations'])
            
            else:  # iot
                # For IoT: balance latency and SLA violations
                for r in param_results:
                    # Calculate a score (lower is better)
                    normalized_latency = r['latency'] / sla_threshold
                    r['score'] = normalized_latency + r['sla_violations']
                
                best_result = min(param_results, key=lambda r: r['score'])
            
            slice_optimal[param_name] = best_result['value']
        
        optimal_params[slice_name] = slice_optimal
    
    return optimal_params

def create_optimized_config(base_config, optimal_params):
    """Create an optimized configuration using the optimal parameters"""
    optimized_config = copy.deepcopy(base_config)
    
    for slice_name, params in optimal_params.items():
        for param_name, value in params.items():
            optimized_config['slices'][slice_name][param_name] = value
    
    return optimized_config

def validate_optimization(base_config, optimized_config):
    """Run a validation comparing the base and optimized configurations"""
    # Save the configurations
    base_config_path = save_config(base_config, "validation_base.yml")
    opt_config_path = save_config(optimized_config, "validation_optimized.yml")
    
    # Run the simulations
    print("Running base configuration simulation...")
    base_log = run_simulation(base_config_path, "validation_base")
    
    print("Running optimized configuration simulation...")
    opt_log = run_simulation(opt_config_path, "validation_optimized")
    
    # Parse the results
    base_results = parse_simulation_results(base_log)
    opt_results = parse_simulation_results(opt_log)
    
    # Calculate improvements
    improvements = {}
    
    # Overall latency improvement
    base_latency = base_results['overall_latency']
    opt_latency = opt_results['overall_latency']
    if base_latency > 0:
        latency_improvement = ((base_latency - opt_latency) / base_latency) * 100
    else:
        latency_improvement = 0
    
    improvements['overall_latency'] = {
        'base': base_latency,
        'optimized': opt_latency,
        'improvement': latency_improvement
    }
    
    # SLA violation improvement
    base_sla = base_results['sla_violations']
    opt_sla = opt_results['sla_violations']
    if base_sla > 0:
        sla_improvement = ((base_sla - opt_sla) / base_sla) * 100
    else:
        sla_improvement = 0
    
    improvements['sla_violations'] = {
        'base': base_sla,
        'optimized': opt_sla,
        'improvement': sla_improvement
    }
    
    # Per-slice latency improvements
    slice_improvements = {}
    for slice_name in base_config['slices']:
        base_slice_latency = base_results['slice_latencies'].get(slice_name, base_latency)
        opt_slice_latency = opt_results['slice_latencies'].get(slice_name, opt_latency)
        
        if base_slice_latency > 0:
            slice_improvement = ((base_slice_latency - opt_slice_latency) / base_slice_latency) * 100
        else:
            slice_improvement = 0
            
        slice_improvements[slice_name] = {
            'base': base_slice_latency,
            'optimized': opt_slice_latency,
            'improvement': slice_improvement
        }
    
    improvements['slice_latencies'] = slice_improvements
    
    # Display results
    print("\n=== Optimization Validation Results ===")
    print(f"Overall Latency: {improvements['overall_latency']['base']:.3f} -> {improvements['overall_latency']['optimized']:.3f} ({improvements['overall_latency']['improvement']:.1f}% improvement)")
    print(f"SLA Violations: {improvements['sla_violations']['base']:.3f} -> {improvements['sla_violations']['optimized']:.3f} ({improvements['sla_violations']['improvement']:.1f}% improvement)")
    
    print("\nPer-Slice Latency Improvements:")
    for slice_name, data in improvements['slice_latencies'].items():
        print(f"  {slice_name}: {data['base']:.3f} -> {data['optimized']:.3f} ({data['improvement']:.1f}% improvement)")
    
    return improvements

def main():
    print("Starting Slice Optimization Framework")
    print("-" * 50)
    
    # Step 1: Find and load the base configuration
    base_config_path = find_config_file()
    with open(base_config_path, 'r') as f:
        base_config = yaml.safe_load(f)
    
    print(f"Loaded base configuration with {len(base_config['slices'])} slices")
    
    # Step 2: Generate test configurations
    print("\nGenerating test configurations...")
    test_configs, config_info = generate_test_configs(base_config)
    print(f"Generated {len(test_configs)} test configurations")
    
    # Step 3: Run simulations and collect results
    print("\nRunning simulations...")
    results = []
    
    for i, (config_name, config) in enumerate(test_configs):
        print(f"\nRunning simulation {i+1}/{len(test_configs)}: {config_name}")
        
        # Save the config
        config_path = save_config(config, f"{config_name}.yml")
        
        # Run the simulation
        log_file = run_simulation(config_path, config_name)
        
        # Parse the results
        sim_results = parse_simulation_results(log_file)
        
        # Combine with configuration info
        full_result = {**config_info[i], **sim_results}
        results.append(full_result)
        
        print(f"Results: Overall latency = {sim_results['overall_latency']:.3f}, SLA violations = {sim_results['sla_violations']:.3f}")
    
    # Step 4: Plot the results
    print("\nPlotting results...")
    plot_results(results, OUTPUT_DIR)
    
    # Step 5: Find optimal configurations
    print("\nFinding optimal configurations...")
    optimal_params = find_optimal_parameters(results, base_config)
    
    print("\nOptimal parameters:")
    for slice_name, params in optimal_params.items():
        print(f"  {slice_name}:")
        for param_name, value in params.items():
            print(f"    {param_name}: {value}")
    
    # Step 6: Create optimized configuration
    print("\nCreating optimized configuration...")
    optimized_config = create_optimized_config(base_config, optimal_params)
    opt_config_path = save_config(optimized_config, "optimized_config.yml")
    print(f"Saved optimized configuration to: {opt_config_path}")
    
    # Step 7: Validate the optimization
    print("\nValidating optimization...")
    validate_optimization(base_config, optimized_config)
    
    print("\nSlice Optimization Process Complete!")
    print(f"Results available in: {OUTPUT_DIR}")

if __name__ == "__main__":
    main()
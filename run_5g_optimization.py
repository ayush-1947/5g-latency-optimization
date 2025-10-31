#!/usr/bin/env python
"""
5G Network Slicing Optimization - Master Script
================================================

This script runs the entire 5G network slicing optimization workflow:
1. Runs the optimization simulations using your existing optimize_slices.py
2. Analyzes the results
3. Generates visualization charts
4. Creates and populates the dashboard
5. Opens the dashboard in a web browser

Run this script with no arguments to execute the complete process:
    python run_5g_optimization.py
"""

import os
import sys
import time
import subprocess
import webbrowser
from pathlib import Path

# Define paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
RESULTS_DIR = os.path.join(BASE_DIR, 'optimization_results')
DASHBOARD_DIR = os.path.join(BASE_DIR, 'dashboard')
IMAGES_DIR = os.path.join(DASHBOARD_DIR, 'images')

# Ensure directories exist
os.makedirs(RESULTS_DIR, exist_ok=True)
os.makedirs(DASHBOARD_DIR, exist_ok=True)
os.makedirs(IMAGES_DIR, exist_ok=True)

def print_header(msg):
    """Print a formatted header."""
    print("\n" + "=" * 80)
    print(f"  {msg}")
    print("=" * 80)

def run_command(cmd, desc):
    """Run a shell command with error handling."""
    print_header(f"STEP: {desc}")
    print(f"Running command: {' '.join(cmd)}")
    
    try:
        subprocess.run(cmd, check=True)
        print(f"✅ {desc} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Error during {desc}: {e}")
        return False
    except FileNotFoundError as e:
        print(f"❌ Command not found: {e}")
        return False

def main():
    """Run the complete 5G network slicing optimization workflow."""
    print_header("5G NETWORK SLICING OPTIMIZATION WORKFLOW")
    print("This script will run the complete workflow from simulation to visualization.")
    
    # Step 1: Run the slice optimization script (your existing implementation)
    if run_command(["python", "optimize_slices.py"], "Slice Optimization"):
        print("Optimization simulations completed.")
    else:
        print("WARNING: Optimization failed. Using existing results if available.")
    
    # Step 2: Run the results analysis
    if run_command(["python", "analyze_optimization_results.py"], "Results Analysis"):
        print("Results analysis completed.")
    else:
        print("WARNING: Analysis failed. Using existing analysis if available.")
    
    # Step 3: Generate visualization charts
    if run_command(["python", "generate_charts.py"], "Chart Generation"):
        print("Chart generation completed.")
    else:
        print("WARNING: Chart generation failed. Dashboard may have missing images.")
    
    # Step 4: Create or update the dashboard
    if not os.path.exists(os.path.join(DASHBOARD_DIR, "index.html")):
        if run_command(["python", "create_dashboard.py"], "Dashboard Creation"):
            print("Dashboard created successfully.")
        else:
            print("ERROR: Dashboard creation failed.")
            return False
    
    # Step 5: Launch the dashboard in a web browser
    dashboard_path = os.path.join(DASHBOARD_DIR, "index.html")
    dashboard_url = Path(dashboard_path).absolute().as_uri()
    
    print_header("LAUNCHING DASHBOARD")
    print(f"Opening dashboard at: {dashboard_url}")
    webbrowser.open(dashboard_url)
    
    print_header("WORKFLOW COMPLETE")
    print("The 5G Network Slicing Optimization process has finished.")
    print(f"Dashboard is available at: {dashboard_url}")
    print("You can view the dashboard anytime by opening the file:")
    print(f"  {dashboard_path}")
    
    return True

if __name__ == "__main__":
    start_time = time.time()
    success = main()
    end_time = time.time()
    
    elapsed = end_time - start_time
    minutes = int(elapsed // 60)
    seconds = int(elapsed % 60)
    
    print(f"\nTotal runtime: {minutes} minutes and {seconds} seconds")
    
    if not success:
        print("❌ Workflow completed with errors. Check the output above for details.")
        sys.exit(1)
    
    print("✅ Workflow completed successfully!")
    sys.exit(0)
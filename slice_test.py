import os
import yaml
import copy
import subprocess

# Get the absolute path to the current directory
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Find the example-input.yml file
def find_config_file():
    # Try multiple possible locations
    possible_paths = [
        os.path.join(BASE_DIR, 'example-input.yml'),
        os.path.join(BASE_DIR, 'slicesim', 'example-input.yml')
    ]
    
    for path in possible_paths:
        if os.path.exists(path):
            print(f"Found configuration file at: {path}")
            return path
    
    raise FileNotFoundError(f"Could not find example-input.yml in any of these locations: {possible_paths}")

def main():
    print("Starting basic test")
    print("-" * 50)
    
    # Find the config file
    config_path = find_config_file()
    
    # Load the config
    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)
    
    print(f"Successfully loaded configuration with {len(config['slices'])} slices")
    
    # Create test directory
    test_dir = os.path.join(BASE_DIR, 'test_output')
    os.makedirs(test_dir, exist_ok=True)
    
    # Save a modified config
    test_config = copy.deepcopy(config)
    test_config['settings']['simulation_time'] = 10  # Very short simulation for testing
    
    test_config_path = os.path.join(test_dir, 'test_config.yml')
    with open(test_config_path, 'w') as f:
        yaml.dump(test_config, f)
    
    print(f"Saved test configuration to: {test_config_path}")
    
    print("\nTest complete! If you see this message, your basic setup is working.")

if __name__ == "__main__":
    main()
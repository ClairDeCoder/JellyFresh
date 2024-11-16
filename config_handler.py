import json
import os

def load_config(config_file):
    """
    Load the configuration file.
    
    Args:
        config_file (str): Path to the configuration file.
        
    Returns:
        dict: Loaded configuration.
    """
    if not os.path.exists(config_file):
        return {"libraries": []}  # Default configuration

    with open(config_file, 'r') as f:
        return json.load(f)


def save_config(config_file, config_data):
    """
    Save the configuration file.
    
    Args:
        config_file (str): Path to the configuration file.
        config_data (dict): Configuration data to save.
    """
    with open(config_file, 'w') as f:
        json.dump(config_data, f, indent=4)

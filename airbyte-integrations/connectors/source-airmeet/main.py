import sys
import json
from source_airmeet.source import SourceAirmeet

def load_config(config_file):
    """ Load the config from a JSON file """
    with open(config_file, 'r') as file:
        return json.load(file)

if __name__ == "__main__":
    # Load the configuration from the config.json file
    config = load_config("secrets/config.json")
    
    # Pass the config dictionary to the check method
    SourceAirmeet().check(config)

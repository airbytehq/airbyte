import tomli
import sys

def validate_toml_files():
    files = [
        'poe-tasks/poetry-source-tasks.toml',
        'airbyte-integrations/connectors/destination-snowflake-cortex/pyproject.toml'
    ]
    
    for file in files:
        with open(file, 'rb') as f:
            tomli.load(f)
    
    print('✅ TOML syntax is valid')

if __name__ == '__main__':
    validate_toml_files()

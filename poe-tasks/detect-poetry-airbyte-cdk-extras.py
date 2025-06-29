#!/usr/bin/env -S uv run --script
#
# dependencies = ["tomli"]

"""
Detect currently installed CDK extras from pyproject.toml file.

This script parses the pyproject.toml file in the specified directory (or current 
directory if not provided) and extracts any extras specified for the airbyte-cdk dependency.

Usage:
    ./detect-poetry-airbyte-cdk-extras.py
    
    ./detect-poetry-airbyte-cdk-extras.py /path/to/connector
    
    [sql]
    
    (no output)
    
    poe -qq get-cdk-extras
"""

import sys
import tomli
from pathlib import Path

def main():
    connector_dir = Path(sys.argv[1]) if len(sys.argv) > 1 else Path('.')
    pyproject_path = connector_dir / 'pyproject.toml'
    
    if not pyproject_path.exists():
        return
    
    with open(pyproject_path, 'rb') as f:
        data = tomli.load(f)
    
    dependencies = data.get('tool', {}).get('poetry', {}).get('dependencies', {})
    cdk_dep = dependencies.get('airbyte-cdk')
    
    if isinstance(cdk_dep, dict):
        extras = cdk_dep.get('extras', [])
        print(f"[{','.join(extras)}]" if extras else "")
    
if __name__ == "__main__":
    main()

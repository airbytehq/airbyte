#!/bin/bash

PACKAGE_NAME="."

# My python version locally is 3.10.10

# Define extras
EXTRAS=( "dev" "sphinx-docs" "file-based" "vector-db-based" )

# Create folder for output
mkdir old_reqs

# Ensure a clean starting point
rm -rf .venv
python -m venv .venv
source .venv/bin/activate

# Install the base package and list installed packages
pip install $PACKAGE_NAME
pip list > base_install.txt

# Loop through each extras option and install
for extra in "${EXTRAS[@]}"; do
    # Clean environment
    deactivate
    rm -rf .venv
    python -m venv .venv
    source .venv/bin/activate
    
    # Install package with the current extras and list installed packages
    pip install "$PACKAGE_NAME[$extra]"
    pip list > "old_reqs/${extra}_install.txt"
done

# Cleanup
deactivate


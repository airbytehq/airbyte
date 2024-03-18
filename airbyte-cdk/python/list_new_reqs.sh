#!/bin/bash
set -e

# Define the directory for new requirements
mkdir -p new_reqs

# Define the extras based on your pyproject.toml configuration
EXTRAS=("dev" "sphinx-docs" "file-based" "vector-db-based")

# Function to remove all poetry environments associated with the project
remove_all_poetry_envs() {
    # List all environments for the project and remove them
    poetry env list | awk '{print $1}' | while read -r env; do
        # These permissions don't work, don't know why
        poetry env remove "$env"
    done
}

get_installed_packages() {
  poetry run poetry show --no-ansi | grep -v "(\!)"
}

# Install base environment with only main dependencies first
remove_all_poetry_envs
poetry install --only main
get_installed_packages > new_reqs/base_install.txt

# Loop through each extras option, install, and save the requirements
for extra in "${EXTRAS[@]}"; do
    # Ensure a clean state before each installation
    remove_all_poetry_envs

    if [ "$extra" == "dev" ]; then
        # For "dev", install all dependencies including development dependencies
        poetry install
        get_installed_packages > "new_reqs/${extra}_install.txt"
    else
        # For other extras, install only main dependencies and the specified extras
        poetry install --only main --extras $extra
        get_installed_packages > "new_reqs/${extra}_install.txt"
    fi
done

# Final cleanup to remove all environments after the script has completed
remove_all_poetry_envs


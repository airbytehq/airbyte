#!/bin/bash

# Recursive function
function recurse_dir {
  for dir in "$1"/*; do
    if [ -d "$dir" ]; then
      # If the directory contains a pyproject.toml file
      if [ -f "$dir/pyproject.toml" ]; then
        echo "Running poetry lock in $dir"
        # Run poetry lock in the directory
        (cd "$dir" && poetry lock)
      fi
      # Recurse into the subdirectory
      recurse_dir "$dir"
    fi
  done
}

# Start from the current directory
recurse_dir .

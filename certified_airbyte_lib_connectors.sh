#!/bin/bash

certified_connectors=()

# Loop through all source-* folders
for dir in airbyte-integrations/connectors/source-*; do
    if [ -d "$dir" ]; then
        # Convert folder name to snake_case
        snake_cased_name=$(echo "$(basename "$dir")" | sed 's/-/_/g')

        # Check for run.py in the snake_cased subfolder
        if [ -f "$dir/$snake_cased_name/run.py" ]; then
            # Check for "supportLevel: certified" in metadata.yaml
            if grep -q "supportLevel: certified" "$dir/metadata.yaml"; then
                certified_connectors+=("$(basename "$dir")")
            fi
        fi
    fi
done

# Print the list of certified connectors
echo "Certified Connectors with run.py:"
for connector in "${certified_connectors[@]}"; do
    echo "$connector"
done

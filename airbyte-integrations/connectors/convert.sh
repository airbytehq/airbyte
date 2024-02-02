#!/bin/bash

# Initialize arrays to keep track of processed and skipped directories
processed_dirs=()
skipped_no_main=()
skipped_no_setup=()
skipped_run_exists=()


# Loop through all directories starting with source-
for dir in source-*/ ; do
    echo "Processing directory: $dir"
    FOLDER_NAME="$dir"
    FOLDER_NAME="${FOLDER_NAME%/}"  # Remove trailing slash
    SNAKE_CASED_FOLDER_NAME=$(echo "$FOLDER_NAME" | sed 's/-/_/g')

    # Check for setup.py
    if [ ! -f "$dir/setup.py" ]; then
        echo "setup.py not found in $dir"
        skipped_no_setup+=("$dir")
        continue
    fi

    # Check for main.py
    if [ ! -f "$dir/main.py" ]; then
        echo "main.py not found in $dir"
        skipped_no_main+=("$dir")
        continue
    fi

    # Check if run.py already exists
    if [ -f "$dir/$SNAKE_CASED_FOLDER_NAME/run.py" ]; then
        echo "run.py already exists in $FOLDER_NAME/$SNAKE_CASED_FOLDER_NAME"
        skipped_run_exists+=("$dir")
        continue
    fi

    # Step 1: Add entry_points to setup.py
    sed -i '' "/setup(/a \\
    entry_points={\\
        \"console_scripts\": [\\
            \"${FOLDER_NAME}=${SNAKE_CASED_FOLDER_NAME}.run:run\",\\
        ],\\
    }," "$FOLDER_NAME/setup.py"

    # Step 2: Create run.py and copy contents from main.py
    mkdir -p "$FOLDER_NAME/$SNAKE_CASED_FOLDER_NAME"
    cp "$FOLDER_NAME/main.py" "$FOLDER_NAME/$SNAKE_CASED_FOLDER_NAME/run.py"
    sed -i '' 's/if __name__ == "__main__":/def run():/' "$FOLDER_NAME/$SNAKE_CASED_FOLDER_NAME/run.py"

    # Step 3: Modify main.py
    echo -e "#\n# Copyright (c) 2023 Airbyte, Inc., all rights reserved.\n#\n\nfrom ${SNAKE_CASED_FOLDER_NAME}.run import run\n\nif __name__ == \"__main__\":\n    run()" > "$FOLDER_NAME/main.py"

    processed_dirs+=("$dir")
done

skipped_no_setup_python=()
skipped_no_setup_other=()
skipped_no_main_python=()
skipped_no_main_other=()

# Function to categorize directories based on metadata.yaml
categorize_based_on_metadata() {
    local dir=$1
    local metadata_file="$dir/metadata.yaml"
    if grep -q "language:python\|language:low-code" "$metadata_file" && ! grep -q "language:java" "$metadata_file"; then
        eval "$2+=('$dir')"  # Add to python/low-code array
    else
        eval "$3+=('$dir')"  # Add to other array
    fi
}

# Categorize skipped_no_setup
for dir in "${skipped_no_setup[@]}"; do
    categorize_based_on_metadata "$dir" "skipped_no_setup_python" "skipped_no_setup_other"
done

# Categorize skipped_no_main
for dir in "${skipped_no_main[@]}"; do
    categorize_based_on_metadata "$dir" "skipped_no_main_python" "skipped_no_main_other"
done


# Print processed and skipped directories
echo "Processed directories:"
printf '%s\n' "${processed_dirs[@]}"

echo "Skipped directories (setup.py not found):"
printf '%s\n' "${skipped_no_setup[@]}"

echo "Skipped directories (main.py not found):"
printf '%s\n' "${skipped_no_main[@]}"

echo "Skipped directories (run.py already exists):"
printf '%s\n' "${skipped_run_exists[@]}"

echo "Skipped directories (setup.py not found, language:python/low-code):"
printf '%s\n' "${skipped_no_setup_python[@]}"

echo "Skipped directories (setup.py not found, other languages):"
printf '%s\n' "${skipped_no_setup_other[@]}"

echo "Skipped directories (main.py not found, language:python/low-code):"
printf '%s\n' "${skipped_no_main_python[@]}"

echo "Skipped directories (main.py not found, other languages):"
printf '%s\n' "${skipped_no_main_other[@]}"
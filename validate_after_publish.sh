#!/bin/bash

# Check if a file path is provided
if [ -z "$1" ]; then
    echo "Please provide a file path."
    exit 1
fi

# Initialize lists
succeeded=()
failure=()

# Temporary Python script filename
tmp_python_script="temp_connector_validation.py"

# Create the Python script
cat > "$tmp_python_script" << EOM
import json
import sys
import airbyte_lib as ab

connector_name = sys.argv[1]
is_certified = sys.argv[3] == 'true'

source = ab.get_connector(f"{connector_name}")

source._get_spec(force_refresh=True) 
print("Got spec without error")

# only do this part for certified connectors
if is_certified:
    config = json.loads(sys.argv[2])
    source.set_config(config)
    source.check()
    streams = source.get_available_streams()

    for stream in streams:
        try:
            print(f"Trying to read from stream {stream}...")
            record = next(source.get_records(stream))
            assert record, "No record returned"
            break
        except Exception as e:
            print(f"Unhandled error occurred when trying to read from {stream}: {e}")
    else:
        raise Exception("Could not read stream")
EOM

# Process each directory
while IFS= read -r directory; do
    directory="${directory%/}"
    echo "Processing directory: $directory"

    # Fetch CI credentials if available (output not printed)
    VERSION=dev ci_credentials "$directory" write-to-storage > /dev/null 2>&1

    # Get the first secret file
    first_secret_file=$(find "./airbyte-integrations/connectors/$directory/secrets/" -type f | head -n 1)
    if [ -z "$first_secret_file" ]; then
        echo "No secret file found in $directory/secrets."
        first_secret_file="/dev/null"
    fi

    # Check if the connector is certified
    metadata_file="./airbyte-integrations/connectors/$directory/metadata.yaml"
    is_certified='false'
    if grep -q "supportLevel: certified" "$metadata_file"; then
        is_certified='true'
    fi

    # Execute Python script and capture output
    if python3 "$tmp_python_script" "$(basename "$directory")" "$(cat "$first_secret_file")" "$is_certified" > "debug-validate-after-publish-$directory.txt" 2>&1; then
        succeeded+=("$directory")
    else
        failure+=("$directory")
    fi

    # Remove .venv folder
    rm -rf ".venv-$directory"
done < "$1"

# Clean up the temporary Python script
rm -f "$tmp_python_script"

# Print results
echo -e "\nSucceeded:"
for dir in "${succeeded[@]}"; do
    echo "$dir"
done

echo -e "\nFailure:"
for dir in "${failure[@]}"; do
    echo "$dir"
done
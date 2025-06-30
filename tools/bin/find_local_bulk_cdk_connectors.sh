#!/bin/bash

# Script to find connectors with local CDK configuration
# Searches for "cdk = 'local'" or "cdk = \"local\"" in airbyteBulkConnector block
# or "useLocalCdk = true" in airbyteJavaConnector block

CONNECTORS_DIR="airbyte-integrations/connectors"
RESULTS=()

echo "Searching for connectors with local CDK configuration..."

# Loop through all directories in the connectors directory
for connector_dir in "$CONNECTORS_DIR"/*; do
  if [ -d "$connector_dir" ]; then
    # Check if build.gradle exists
    if [ -f "$connector_dir/build.gradle" ]; then
      connector_name=$(basename "$connector_dir")

      # Search for cdk = 'local' or cdk = "local" in airbyteBulkConnector block
      if grep -q "airbyteBulkConnector" "$connector_dir/build.gradle" && grep -q "cdk *= *['\"]local['\"]" "$connector_dir/build.gradle"; then
        RESULTS+=("$connector_name (airbyteBulkConnector with cdk = local)")
      fi

      # Search for useLocalCdk = true in airbyteJavaConnector block
      if grep -q "airbyteJavaConnector" "$connector_dir/build.gradle" && grep -q "useLocalCdk *= *true" "$connector_dir/build.gradle"; then
        RESULTS+=("$connector_name (airbyteJavaConnector with useLocalCdk = true)")
      fi
    fi
  fi
done

# Print results
if [ ${#RESULTS[@]} -eq 0 ]; then
  echo "No connectors with local CDK configuration found."
else
  echo "Found ${#RESULTS[@]} connectors with local CDK configuration:"
  for result in "${RESULTS[@]}"; do
    echo "- $result"
  done
fi
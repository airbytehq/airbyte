#!/bin/bash

# Script to find connectors with local CDK configuration
# Searches for "cdk = 'local'" or "cdk = \"local\"" in airbyteBulkConnector block
# Ignore the old CDK as none are on local.

# Default values
CONNECTORS_DIR="airbyte-integrations/connectors"
DOWNLOAD_SECRETS=false
RESULTS=()

# Function to display usage information
usage() {
  echo "Usage: $0 [OPTIONS]"
  echo "Find connectors with local CDK configuration and optionally download their secrets."
  echo
  echo "Options:"
  echo "  -h, --help     Display this help message and exit"
  echo "  -s, --secret   Download secrets for connectors with local CDK"
  echo
  echo "By default, the script lists all connectors with local CDK configuration."
  echo "With --secret flag, it also downloads secrets for those connectors using:"
  echo "  VERSION=dev ci_credentials [connector-name] write-to-storage"
}

# Parse command line arguments
while [[ $# -gt 0 ]]; do
  case "$1" in
    -h|--help)
      usage
      exit 0
      ;;
    -s|--secret)
      DOWNLOAD_SECRETS=true
      shift
      ;;
    *)
      echo "Unknown option: $1"
      usage
      exit 1
      ;;
  esac
done

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
    fi
  fi
done

# Print results
if [ ${#RESULTS[@]} -eq 0 ]; then
  echo "No connectors with local CDK configuration found."
else
  echo "Found ${#RESULTS[@]} connectors with local CDK configuration:"
  for result in "${RESULTS[@]}"; do
    # Extract connector name without the description
    connector=$(echo "$result" | cut -d' ' -f1)
    echo "- $result"

    # Download secrets if --secret flag is provided
    if [ "$DOWNLOAD_SECRETS" = true ]; then
      echo "  Downloading secrets for $connector..."
      VERSION=dev ci_credentials "$connector" write-to-storage
      if [ $? -eq 0 ]; then
        echo "  ✅ Secrets downloaded successfully for $connector"
      else
        echo "  ❌ Failed to download secrets for $connector"
      fi
    fi
  done
fi

# If secrets were downloaded, provide a summary
if [ "$DOWNLOAD_SECRETS" = true ]; then
  if [ ${#RESULTS[@]} -gt 0 ]; then
    echo
    echo "Secret download summary:"
    echo "------------------------"
    echo "Downloaded secrets for ${#RESULTS[@]} connectors with local CDK configuration."
    echo "Secrets are stored in each connector's 'secrets' directory."
  fi
fi
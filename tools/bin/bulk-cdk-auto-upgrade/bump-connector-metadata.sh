#!/usr/bin/env bash

set -euo pipefail

# Performs a patch version bump in the metadata.yaml of the given connector.
# Prints the new version number.
# Usage: tools/bin/bulk-cdk-auto-upgrade/bump-connector-metadata.sh destination-dev-null

connector_name=$1

metadata_file="airbyte-integrations/connectors/$connector_name/metadata.yaml"

# Extract current version
current_version=$(yq '.data.dockerImageTag' "$metadata_file")

# Parse version components
IFS='.' read -r major minor patch <<< "$current_version"

# Increment patch version
new_patch=$((patch + 1))
new_version="${major}.${minor}.${new_patch}"

# Update metadata.yaml
yq --inplace --prettyPrint ".data.dockerImageTag = \"${new_version}\"" "$metadata_file"

echo "$new_version"

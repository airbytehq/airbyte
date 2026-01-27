#!/usr/bin/env bash

set -euo pipefail

# Performs a patch version bump in the metadata.yaml of the given connector.
# Prints the new version number.
# Usage: tools/bin/bulk-cdk/auto-upgrade/bump-connector-metadata.sh destination-dev-null

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
# Don't use `yq` for this. yq introduces unrelated diffs and does not preserve formatting.
# In particular, yq may introduce diffs that cause our formatter to complain.
# Don't use `-i` b/c it's not platform-agnostic (macos requires `-i ''`, but that doesn't work on linux)
sed "s/dockerImageTag: ${current_version}/dockerImageTag: ${new_version}/" "$metadata_file" > "$metadata_file.tmp"
mv "$metadata_file.tmp" "$metadata_file"

echo "$new_version"

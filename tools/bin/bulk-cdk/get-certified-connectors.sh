#!/usr/bin/env bash

set -euo pipefail

# List all certified connectors, which are using the bulk CDK, and don't have a weird version number (e.g. -rc suffix).
# And also source-datagen + destination-dev-null.
# Prints the result as a JSON array.
#
# Usage:
#   get-certified-connectors.sh [filter]
#
# Arguments:
#   filter - Optional. One of: "sources", "destinations", or "all" (default)
#            "sources" - only return source-* connectors
#            "destinations" - only return destination-* connectors
#            "all" - return all connectors

FILTER="${1:-all}"

connectors=()

# datagen and dev-null aren't certified, but we should probably keep them on the latest CDK anyway
if [[ "$FILTER" == "all" || "$FILTER" == "destinations" ]]; then
  default_destinations=(destination-dev-null)
  for connector in "${default_destinations[@]}"; do
    metadata_file="airbyte-integrations/connectors/${connector}/metadata.yaml"
    if test -f "$metadata_file"; then
      if echo $(yq '.data.dockerImageTag' "$metadata_file") | grep -qE '^[0-9]+\.[0-9]+\.[0-9]+$'; then
        connectors+=("$connector")
      fi
    fi
  done
fi

if [[ "$FILTER" == "all" || "$FILTER" == "sources" ]]; then
  default_sources=(source-datagen)
  for connector in "${default_sources[@]}"; do
    metadata_file="airbyte-integrations/connectors/${connector}/metadata.yaml"
    if test -f "$metadata_file"; then
      if echo $(yq '.data.dockerImageTag' "$metadata_file") | grep -qE '^[0-9]+\.[0-9]+\.[0-9]+$'; then
        connectors+=("$connector")
      fi
    fi
  done
fi

for dir in airbyte-integrations/connectors/*; do
  connector_name=$(basename "$dir")

  # Apply filter
  if [[ "$FILTER" == "sources" && ! "$connector_name" == source-* ]]; then
    continue
  fi
  if [[ "$FILTER" == "destinations" && ! "$connector_name" == destination-* ]]; then
    continue
  fi

  metadata_file="${dir}/metadata.yaml"
  build_gradle="${dir}/build.gradle"
  build_gradle_kts="${dir}/build.gradle.kts"

  # If metadata.yaml exists and says we're certified
  if (test -f "$metadata_file") && (test $(yq '.data.supportLevel' "$metadata_file") = 'certified'); then
    # If we have a gradle buildscript using the bulk connector plugin
    if (test -f "$build_gradle" && grep -q "airbyte-bulk-connector" "$build_gradle") || \
        (test -f "$build_gradle_kts" && grep -q "airbyte-bulk-connector" "$build_gradle_kts"); then
      # If we're on a "normal" version (e.g. 12.34.56)
      if echo $(yq '.data.dockerImageTag' "$metadata_file") | grep -qE '^[0-9]+\.[0-9]+\.[0-9]+$'; then
        connectors+=("$connector_name")
      fi
    fi
  fi
done

# Handle empty array case
if [[ ${#connectors[@]} -eq 0 ]]; then
  echo "[]"
  exit 0
fi

# Nonobvious `printf | jq | jq` thing here:
# Print each element of the array on a separate line
# -> jq converts each line to a JSON string (i.e. wrap in double quotes)
# -> jq reads those lines and wraps them into a JSON array (compact-output is needed for compatibility with github's output format)
json_array=$(printf '%s\n' "${connectors[@]}" | jq --raw-input . | jq --compact-output --slurp .)
echo "$json_array"

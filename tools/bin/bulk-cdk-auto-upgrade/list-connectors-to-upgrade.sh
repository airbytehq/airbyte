#!/usr/bin/env bash

set -euo pipefail

# List all certified connectors, which are using the bulk CDK.
# And also source-datagen + destination-dev-null.
# Prints the result as a JSON array.

# datagen and dev-null aren't certified, but we should probably keep them on the latest CDK anyway
connectors=(destination-dev-null source-datagen)
for dir in airbyte-integrations/connectors/*; do
  metadata_file="${dir}/metadata.yaml"
  build_gradle="${dir}/build.gradle"
  build_gradle_kts="${dir}/build.gradle.kts"

  # If metadata.yaml exists and says we're certified
  if (test -f "$metadata_file") && (test $(yq '.data.supportLevel' "$metadata_file") = 'certified'); then
    # If we have a gradle buildscript using the bulk connector plugin
    if (test -f "$build_gradle" && grep -q "airbyte-bulk-connector" "$build_gradle") || \
        (test -f "$build_gradle_kts" && grep -q "airbyte-bulk-connector" "$build_gradle_kts"); then
      connector_name=$(basename "$dir")
      connectors+=("$connector_name")
    fi
  fi
done

# Nonobvious `printf | jq | jq` thing here:
# Print each element of the array on a separate line
# -> jq converts each line to a JSON string (i.e. wrap in double quotes)
# -> jq reads those lines and wraps them into a JSON array (compact-output is needed for compatibility with github's output format)
json_array=$(printf '%s\n' "${connectors[@]}" | jq --raw-input . | jq --compact-output --slurp .)
echo "$json_array"

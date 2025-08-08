#!/usr/bin/env bash

# This script takes any number of command-line arguments in the format `--name <connector_name>`
# and prints some key-value pairs, formatted as Github output variables.
# For example, `./parse-connector-name-args.sh --name source-faker --name destination-bigquery` will print:
# connectors-to-publish={"connector":["source-faker","destination-bigquery"]}
# connectors-to-publish-jvm={"connector":["destination-bigquery"]}
# (assuming that source-faker is a non-JVM connector, and destination-bigquery is a JVM connector)

source "${BASH_SOURCE%/*}/lib/util.sh"

source "${BASH_SOURCE%/*}/lib/parse_args.sh"

connectors_jvm=()
for connector in "${connectors[@]}"
do
  meta="${CONNECTORS_DIR}/${connector}/metadata.yaml"
  if ! test -f "$meta"; then
    echo "Error: metadata.yaml not found for ${connector}" >&2
    exit 1
  fi

  if grep -qE 'language:\s*java' "$meta"; then
    connectors_jvm+=($connector)
  fi
done

# `printf '%s\n' "${arr[@]}"` prints each array item on a new line.
# `jq --raw-input .` reads each line as a string value, and writes that value back out as a JSON string (i.e. wrapped in double quotes).
#   (this also handles JSON escaping, though hopefully that's not needed for any connector name...)
# `jq --compact-output --slurp .` then reads each line as a JSON value and writes them back out as a JSON array.
#   `--compact-output` makes jq minify the output, rather than prettyprinting it.
#   `--slurp` makes jq parse each line into a JSON value, then combine them all into an array.
# We then wrap the entire thing in a JSON object.
connectors_output='{"connector":'$(printf '%s\n' "${connectors[@]}" | jq --raw-input . | jq --compact-output --slurp .)'}'
connectors_jvm_output='{"connector":'$(printf '%s\n' "${connectors_jvm[@]}" | jq --raw-input . | jq --compact-output --slurp .)'}'

echo "connectors-to-publish=$connectors_output"
echo "connectors-to-publish-jvm=$connectors_jvm_output"

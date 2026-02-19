#!/usr/bin/env bash

# This script takes any number of command-line arguments in the format `--name <connector_name>`
# and prints some key-value pairs, formatted to be used as a GitHub output variable for matrix builds.
# For example, `./parse-connector-name-args.sh --name source-faker --name destination-bigquery` will print:
# {"connector":["source-faker","destination-bigquery"]}
connectors=()

while [[ $# -gt 0 ]]; do
  case "$1" in
    --name=*)
      connectors+=("${1#*=}")
      shift
      ;;
    --name)
      connectors+=("$2")
      shift 2
      ;;
    --*)
      echo "Error: Unknown flag $1" >&2
      exit 1
      ;;
    *)
      connectors+=("$1")
      shift
      ;;
  esac
done

# `printf '%s\n' "${arr[@]}"` prints each array item on a new line.
# `jq --raw-input .` reads each line as a string value, and writes that value back out as a JSON string (i.e. wrapped in double quotes).
#   (this also handles JSON escaping, though hopefully that's not needed for any connector name...)
# `jq --compact-output --slurp .` then reads each line as a JSON value and writes them back out as a JSON array.
#   `--compact-output` makes jq minify the output, rather than prettyprinting it.
#   `--slurp` makes jq parse each line into a JSON value, then combine them all into an array.
# We then wrap the entire thing in a JSON object.
connectors_output='{"connector":'$(printf '%s\n' "${connectors[@]}" | jq --raw-input . | jq --compact-output --slurp .)'}'

echo "$connectors_output"

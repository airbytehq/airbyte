# A collection of utility functions and constants.
# Usage (assuming your script is in `poe-tasks`): Add `source "${BASH_SOURCE%/*}/lib/util.sh"` to your script.
# You can't just `source lib/util.sh`, because the current working directory probably isn't `poe-tasks`.

CONNECTORS_DIR="airbyte-integrations/connectors"

# ---------- helper: collect connector names ----------
# Read a list of connector names from a variable, or parse stdin.
# Expects that you have populated a $connectors variable as an array.
# If you sourced the parse_args.sh script, this is already handled for you.
get_connectors() {
  if [ "${#connectors[@]}" -gt 0 ]; then
      # only look at non-empty strings
      for c in "${connectors[@]}"; do
          [[ -n "$c" ]] && printf "%s\n" "$c"
      done
  else
    # read JSON from stdin
    if [ -t 0 ]; then
      echo "Error:  No --name given and nothing piped to stdin." >&2
      exit 1
    fi
    # select only non-empty strings out of the JSON array
    jq -r '.connector[] | select(. != "")'
  fi
}

# Generate the prerelease image tag (e.g. `1.2.3-dev.abcde12345`).
generate_dev_tag() {
  local base="$1"
  # force a 10-char short hash to match existing airbyte-ci behaviour.
  local hash
  hash=$(git rev-parse --short=10 HEAD)
  echo "${base}-dev.${hash}"
}

# A collection of utility functions and constants.
# Usage (assuming your script is in `poe-tasks`): Add `source "${BASH_SOURCE%/*}/lib/util.sh"` to your script.
# You can't just `source lib/util.sh`, because the current working directory probably isn't `poe-tasks`.

CONNECTORS_DIR="airbyte-integrations/connectors"
DOCS_BASE_DIR="docs/integrations"
METADATA_SERVICE_PATH='airbyte-ci/connectors/metadata_service/lib'

# Usage: connector_docs_path "source-foo"
# Returns a string "docs/integrations/sources/foo.md"
connector_docs_path() {
  # First, remove -strict-encrypt suffix since these connectors
  # share documentation with their base connector
  local connector_name="$1"
  connector_name=$(echo "$connector_name" | sed -r 's/-strict-encrypt$//')

  # The regex '^(source|destination)-(.*)' matches strings like source-whatever or destination-something-like-this,
  # capturing the connector type (source/destination) and the connector name (whatever / something-like-this).
  # We then output '\1s/\2.md', which inserts the captured values as `\1` and `\2`.
  # This produces a string like `sources/whatever.md`.
  # Then we prepend the 'docs/integrations/' path.
  echo $DOCS_BASE_DIR/$(echo $connector_name | sed -r 's@^(source|destination)-(.*)@\1s/\2.md@')
}

# Typically called immediately after sourcing parse_args.sh
# Throws an error if zero or multiple `--name` flags were passed.
# If exactly one `--name` flag was passed, return that connector.
get_only_connector() {
  # "${#connectors[@]}" is the length of the array
  if test "${#connectors[@]}" -eq 0; then
    echo 'Missing `--name <connector_name>` argument' >&2
    exit 1
  fi
  if test "${#connectors[@]}" -gt 1; then
    echo 'Expected to get exactly 1 connector. Got:' >&2
    printf "%s\n" "${connectors[@]}" >&2
    exit 1
  fi
  # we've validated that the array contains exactly one element,
  # so get the first element.
  echo "${connectors[@]:0:1}"
}

# Generate the prerelease image tag (e.g. `1.2.3-dev.abcde12345`).
generate_dev_tag() {
  local base="$1"
  # force a 10-char short hash to match existing airbyte-ci behaviour.
  local hash
  hash=$(git rev-parse --short=10 HEAD)
  echo "${base}-dev.${hash}"
}

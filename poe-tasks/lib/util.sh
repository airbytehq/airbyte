# A collection of utility functions and constants.
# Usage (assuming your script is in `poe-tasks`): Add `source "${BASH_SOURCE%/*}/lib/util.sh"` to your script.
# You can't just `source lib/util.sh`, because the current working directory probably isn't `poe-tasks`.

CONNECTORS_DIR="airbyte-integrations/connectors"
DOCS_ROOT="docs"
DOCS_BASE_DIR="$DOCS_ROOT/integrations"
METADATA_SERVICE_PATH='airbyte-ci/connectors/metadata_service/lib'

# Usage: connector_docs_path "source-foo"
# Returns a string "docs/integrations/sources/foo.md"
connector_docs_path() {
  # First, remove -strict-encrypt suffix since these connectors
  # share documentation with their base connector
  local connector_name="$1"
  local is_enterprise="$2"
  connector_name=$(echo "$connector_name" | sed -r 's/-strict-encrypt$//')

  if [ "$is_enterprise" = "true" ]; then
    docs_path="$DOCS_BASE_DIR/enterprise-connectors/$connector_name.md"
  else
    # The regex '^(source|destination)-(.*)' matches strings like source-whatever or destination-something-like-this,
    # capturing the connector type (source/destination) and the connector name (whatever / something-like-this).
    # We then output '\1s/\2.md', which inserts the captured values as `\1` and `\2`.
    # This produces a string like `sources/whatever.md`.
    # Then we prepend the 'docs/integrations/' path.
    docs_path=$DOCS_BASE_DIR/$(echo $connector_name | sed -r 's@^(source|destination)-(.*)@\1s/\2.md@')
  fi

  if ! test -f "$docs_path"; then
      echo 'Connector documentation file does not exist:' "$docs_path" >&2
  fi

  echo "$docs_path"
}

# Expects that you have populated a $connectors variable as an array.
# If you sourced the parse_args.sh script, this is already handled for you.
# If $connectors has exactly one element, return that element.
# Otherwise, prints an error and crashes the script.
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

# Authenticate to gcloud using the contents of a variable.
# That variable should contain a JSON-formatted GCP service account key.
gcloud_activate_service_account() {
  touch /tmp/gcloud_creds.json
  # revoke access to this file from group/other (`go=` means "for Group/Other, set permissions to nothing")
  # (i.e. only the current user can interact with it)
  chmod go= /tmp/gcloud_creds.json
  # echo -E prevents echo from rendering \n into actual newlines.
  echo -E "$1" > /tmp/gcloud_creds.json
  gcloud auth activate-service-account --key-file /tmp/gcloud_creds.json
}

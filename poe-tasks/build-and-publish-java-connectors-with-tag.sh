#!/usr/bin/env bash
# Usage examples:
#   ./get-modified-connectors.sh --prev-commit --json | ./build-and-publish-java-connectors-with-tag.sh
#
# Specific to this script:
#   1) Default (pre-release) on a single connector
#   ./build-and-publish-java-connectors-with-tag.sh foo-conn
#   ./build-and-publish-java-connectors-with-tag.sh --name=foo-conn
#
#   2) Explicit main-release with multiple connectors
#   ./build-and-publish-java-connectors-with-tag.sh --main-release foo-conn bar-conn
#
#   3) Pre-release (dev tag) via JSON pipe
#   echo '{"connector":["foo-conn","bar-conn"]}' | ./build-and-publish-java-connectors-with-tag.sh --pre-release
#
#   4) Mixed: positional + pre-release
#   ./build-and-publish-java-connectors-with-tag.sh --pre-release foo-conn
#
#   5) Enable actual publishing (default is dry-run mode)
#   ./build-and-publish-java-connectors-with-tag.sh --publish foo-conn
set -euo pipefail

CONNECTORS_DIR="airbyte-integrations/connectors"

# ── Rollout whitelist: only connectors listed here will be built/published
# Function to check if a connector is in the whitelist
is_in_whitelist() {
  local connector="$1"
  case "$connector" in
    destination-azure-blob-storage|\
    destination-bigquery|\
    destination-clickhouse-strict-encrypt|\
    destination-clickhouse|\
    destination-csv|\
    destination-databricks|\
    destination-dev-null|\
    destination-dynamodb|\
    destination-elasticsearch-strict-encrypt|\
    destination-elasticsearch|\
    destination-gcs|\
    destination-kafka|\
    destination-local-json|\
    destination-mongodb-strict-encrypt|\
    destination-mongodb|\
    destination-mysql-strict-encrypt|\
    destination-mysql|\
    destination-oracle-strict-encrypt|\
    destination-oracle|\
    destination-postgres-strict-encrypt|\
    destination-postgres|\
    destination-redis|\
    destination-redshift|\
    destination-s3-data-lake|\
    destination-s3|\
    destination-singlestore|\
    destination-snowflake|\
    destination-starburst-galaxy|\
    destination-teradata|\
    destination-yellowbrick|\
    source-e2e-test|\
    source-postgres|\
    source-mysql)
      return 0
      ;;
    *)
      return 1
      ;;
  esac
}

# ------ Defaults & arg parsing -------
publish_mode="pre-release"
do_publish=false
connectors=()

while [[ $# -gt 0 ]]; do
  case "$1" in
    -h|--help)
      sed -n '1,20p' "$0"
      exit 0
      ;;
    --main-release)
      publish_mode="main-release"
      shift
      ;;
    --pre-release)
      publish_mode="pre-release"
      shift
      ;;
    --publish)
      do_publish=true
      shift
      ;;
    --name=*)
      connectors=("${1#*=}")
      shift
      ;;
    --name)
      connectors=("$2")
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

# ---------- helper: collect connector names ----------
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

generate_dev_tag() {
  local base="$1"
  # force a 10-char short hash to match existing airbyte-ci behaviour.
  local hash
  hash=$(git rev-parse --short=10 HEAD)
  echo "${base}-dev.${hash}"
}

# Function to compare version strings
# Returns 0 if version1 > version2
# Returns 1 if version1 <= version2
version_gt() {
  local v1="$1"
  local v2="$2"

  # If versions are identical, return 1 (not greater)
  if [[ "$v1" == "$v2" ]]; then
    return 1
  fi

  # Extract components (assuming semantic versioning) on the . separator.
  local IFS=.
  local i v1_array=($v1) v2_array=($v2)

  # Compare each component
  for ((i=0; i<${#v1_array[@]} || i<${#v2_array[@]}; i++)); do
    # Default to 0 if component doesn't exist. 1.2 -> 1.2.0
    local v1_comp=${v1_array[i]:-0}
    local v2_comp=${v2_array[i]:-0}

    # Remove any non-numeric suffix (like -alpha, -beta, etc.) for simplicity.
    v1_comp=$(echo "$v1_comp" | sed -E 's/([0-9]+).*/\1/')
    v2_comp=$(echo "$v2_comp" | sed -E 's/([0-9]+).*/\1/')

    # Compare numerically
    if ((10#$v1_comp > 10#$v2_comp)); then
      return 0  # version1 > version2
    elif ((10#$v1_comp < 10#$v2_comp)); then
      return 1  # version1 < version2
    fi
    # If equal, continue to next component
  done

  # If we get here, all components were equal or v1 ran out of components
  return 1  # version1 <= version2
}

# ---------- main loop ----------
while read -r connector; do
  # only publish if connector is in whitelist
  if ! is_in_whitelist "$connector"; then
    echo "ℹ️  Skipping '$connector'; not in rollout whitelist"
    continue
  fi

  meta="${CONNECTORS_DIR}/${connector}/metadata.yaml"
  if [[ ! -f "$meta" ]]; then
    echo "Error: metadata.yaml not found for ${connector}" >&2
    exit 1
  fi

  base_tag=$(yq -r '.data.dockerImageTag' "$meta")
  if [[ -z "$base_tag" || "$base_tag" == "null" ]]; then
    echo "Error:  dockerImageTag missing in ${meta}" >&2
    exit 1
  fi

  if [[ "$publish_mode" == "main-release" ]]; then
    # Check if version has increased for main releases
    previous_version=""
    # Try to get the previous version from git history
    previous_version=$(git show HEAD~1:"${meta}" 2>/dev/null | yq -r '.data.dockerImageTag' || echo "")

    if [ -n "$previous_version" ]; then
      # Check if current version is greater than previous version
      if ! version_gt "$base_tag" "$previous_version"; then
        echo "ℹ️  Skipping '$connector'; version not increased (current: $base_tag, previous: $previous_version)"
        continue
      fi

      echo "✅ Publishing '$connector'; version increased: $previous_version -> $base_tag"
    else
      echo "✅ Publishing '$connector'; no previous version found, treating as new connector"
    fi

    docker_tag="$base_tag"
  else
    docker_tag=$(generate_dev_tag "$base_tag")
  fi

  if $do_publish; then
    echo "Building & publishing ${connector} with tag ${docker_tag}"
    ./gradlew -Pdocker.publish \
              -DciMode=true \
              -Psbom=false \
              -Pdocker.tag="${docker_tag}" \
              ":${CONNECTORS_DIR//\//:}:${connector}:assemble"
  else
    echo "DRY RUN: Would build & publish ${connector} with tag ${docker_tag}"
  fi
done < <(get_connectors)
if $do_publish; then
  echo "Done building & publishing."
else
  echo "DRY RUN: Done building. No images were published. Use --publish flag to enable publishing."
fi

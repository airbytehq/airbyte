#!/usr/bin/env bash
# This script builds and optionally publishes Java connector Docker images.
#
# Flag descriptions:
#   --main-release: Publishes images with the exact version from metadata.yaml.
#                   Only publishes if the image does not exists on Dockerhub.
#                   Used for production releases on merge to master.
#
#   --pre-release:  Publishes images with a dev tag (version-dev.githash).
#                   Only publishes if the image does not exists on Dockerhub.
#                   Used for development/testing purposes.
#
#   --publish:      Actually publishes the images. Without this flag, the script runs in dry-run mode
#                   and only shows what would be published without actually publishing.
#
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
    destination-csv|\
    destination-clickhouse|\
    destination-clickhouse-strict-encrypt|\
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
      sed -n '1,34p' "$0"
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

dockerhub_tag_exists() {
  local image="$1"   # e.g. airbyte/destination-postgres
  local tag="$2"     # e.g. 0.7.27
  local max_attempts=5
  local delay=1

  local namespace repo status url
  namespace=$(cut -d/ -f1 <<<"$image")
  repo=$(cut -d/ -f2 <<<"$image")
  url="https://registry.hub.docker.com/v2/repositories/${namespace}/${repo}/tags/${tag}/"

  for ((attempt=1; attempt<=max_attempts; attempt++)); do
    # -s silences progress bar, -o specifies the output, and -w extract only http_code.
    # essentially keep things clean.
    status=$(curl -s -o /dev/null -w "%{http_code}" "$url")

    if [[ "$status" == "200" ]]; then
      return 0  # tag exists
    elif [[ "$status" == "404" ]]; then
      return 1  # tag does not exist
    else
      echo "⚠️  Docker Hub check failed (status $status), retrying in $delay seconds... ($attempt/$max_attempts)" >&2
      sleep "$delay"
      delay=$((delay * 2))  # exponential backoff
    fi
  done

  # Blow up to be safe.
  echo "❌ Failed to contact Docker Hub after $max_attempts attempts. Exiting to be safe." >&2
  exit 1
}

generate_dev_tag() {
  local base="$1"
  # force a 10-char short hash to match existing airbyte-ci behaviour.
  local hash
  hash=$(git rev-parse --short=10 HEAD)
  echo "${base}-dev.${hash}"
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
    docker_tag="$base_tag"
  else
    docker_tag=$(generate_dev_tag "$base_tag")
  fi

  if $do_publish; then
    echo "Building & publishing ${connector} with tag ${docker_tag}"

    if dockerhub_tag_exists "airbyte/${connector}" "$docker_tag"; then
      echo "ℹ️  Skipping publish — tag airbyte/${connector}:${docker_tag} already exists."
      continue
    fi

    echo "airbyte/${connector}:${docker_tag} image does not exists on Docker. Publishing..."
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

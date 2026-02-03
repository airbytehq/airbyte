#!/usr/bin/env bash

# This script builds and optionally publishes Java connector Docker images.
# Usage: ./build-and-publish-java-connectors-with-tag.sh --name <name> --release-type [pre-release | main-release] [--publish]
#
# Flag descriptions:
#   --name <name>:    Specifies the connector name (e.g., destination-bigquery).
#                    
#   --release-type:   Specifies the release type:
#                     - pre-release: Builds with a preview tag (version-preview.githash).
#                     - main-release: Builds with the exact version from metadata.yaml.
#                     Defaults to pre-release if not specified.
#
#   --publish:      Actually publishes the images. Without this flag, the script runs in dry-run mode
#                   and only shows what would be published without actually publishing.
#
# Usage examples:
#   ./build-and-publish-java-connectors-with-tag.sh --name destination-bigquery --pre-release --publish
#
# Specific to this script:
#   1) Default (pre-release) on a single connector
#   ./build-and-publish-java-connectors-with-tag.sh foo-conn
#   ./build-and-publish-java-connectors-with-tag.sh --name=foo-conn
#
#   2) Mixed: positional + pre-release
#   ./build-and-publish-java-connectors-with-tag.sh --release-type=pre-release foo-conn
#
#   3) Enable actual publishing (default is dry-run mode)
#   ./build-and-publish-java-connectors-with-tag.sh --publish foo-conn
set -euo pipefail

source "${BASH_SOURCE%/*}/lib/util.sh"

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

source "${BASH_SOURCE%/*}/lib/parse_args.sh"
connector=$(get_only_connector)

meta="${CONNECTORS_DIR}/${connector}/metadata.yaml"
if [[ ! -f "$meta" ]]; then
  echo "Error: metadata.yaml not found for ${connector}" >&2
  exit 1
fi

# Check if this is a Java connector
if ! grep -qE 'language:\s*java' "$meta"; then
  echo "ℹ️  Skipping ${connector} — this script only supports JVM connectors for now."
  continue
fi

base_tag=$(yq -r '.data.dockerImageTag' "$meta")
if [[ -z "$base_tag" || "$base_tag" == "null" ]]; then
  echo "Error:  dockerImageTag missing in ${meta}" >&2
  exit 1
fi

docker_repository=$(yq -r '.data.dockerRepository' "$meta")
if [[ -z "$docker_repository" || "$docker_repository" == "null" ]]; then
  echo "Error:  dockerRepository missing in ${meta}" >&2
  exit 1
fi

if [[ "$publish_mode" == "main-release" ]]; then
  docker_tag="$base_tag"
else
  docker_tag=$(generate_dev_tag "$base_tag")
fi

if $do_publish; then
  echo "Building & publishing ${connector} to ${docker_repository} with tag ${docker_tag}"

  if dockerhub_tag_exists "${docker_repository}" "$docker_tag"; then
    echo "ℹ️  Skipping publish — tag ${docker_repository}:${docker_tag} already exists."
    exit
  fi

  echo "${docker_repository}:${docker_tag} image does not exists on Docker. Publishing..."
  ./gradlew -Pdocker.publish \
            -DciMode=true \
            -Psbom=false \
            -Pdocker.tag="${docker_tag}" \
            ":${CONNECTORS_DIR//\//:}:${connector}:assemble"
else
  echo "DRY RUN: Would build & publish ${connector} with tag ${docker_tag}"
fi
if $do_publish; then
  echo "Done building & publishing."
else
  echo "DRY RUN: Done building. No images were published. Use --publish flag to enable publishing."
fi

#!/usr/bin/env bash

# Uploads the java tar for java connectors.
# Usage: ./poe-tasks/upload-java-connector-tar-file.sh --name destination-bigquery --release-type <pre-release|main-release>
# You must have set the env var GCS_CREDENTIALS, which contains a JSON-formatted GCP service account key.
# GCS_CREDENTIALS needs write access to `gs://$metadata_bucket/resources/java`.
set -euo pipefail

source "${BASH_SOURCE%/*}/lib/util.sh"
source "${BASH_SOURCE%/*}/lib/parse_args.sh"

metadata_bucket="dev-airbyte-cloud-connector-metadata-service-2"
connector=$(get_only_connector)
tar_file_path="${CONNECTORS_DIR}/${connector}/build/distributions/airbyte-app.tar"

if ! test "$GCS_CREDENTIALS"; then
  echo "GCS_CREDENTIALS environment variable must be set" >&2
  exit 1
fi

# Figure out the tag that we're working on (i.e. handle the prerelease case)
meta="${CONNECTORS_DIR}/${connector}/metadata.yaml"
base_tag=$(yq -r '.data.dockerImageTag' "$meta")
if test -z "$base_tag" || test "$base_tag" = "null"; then
  echo "Error: dockerImageTag missing in ${meta}" >&2
  exit 1
fi
if test "$publish_mode" = "main-release"; then
  docker_tag="$base_tag"
else
  docker_tag=$(generate_dev_tag "$base_tag")
fi

gcloud_activate_service_account "$GCS_CREDENTIALS"
gcloud storage cp "$tar_file_path" "gs://${metadata_bucket}/resources/java/${connector}/${docker_tag}/"

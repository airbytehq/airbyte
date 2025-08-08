#!/usr/bin/env bash
set -euo pipefail

# Uploads the metadata (+SBOM+spec cache) to GCS.
# Usage: ./poe-tasks/upload-connector-metadata.sh --name destination-bigquery [--pre-release] [--main-release]
# You must have three environment variables set (GCS_CREDENTIALS, METADATA_SERVICE_GCS_CREDENTIALS, SPEC_CACHE_GCS_CREDENTIALS),
# each containing a JSON-formatted GCP service account key.
# SPEC_CACHE_GCS_CREDENTIALS needs write access to `gs://$spec_cache_bucket/specs`.
# METADATA_SERVICE_GCS_CREDENTIALS needs write access to `gs://$metadata_bucket/sbom`.
# GCS_CREDENTIALS needs write access to `gs://$metadata_bucket/metadata`.

source "${BASH_SOURCE%/*}/lib/util.sh"

source "${BASH_SOURCE%/*}/lib/parse_args.sh"
connector=$(get_only_connector)

if ! test "$SPEC_CACHE_GCS_CREDENTIALS"; then
  echo "SPEC_CACHE_GCS_CREDENTIALS environment variable must be set" >&2
  exit 1
fi
if ! test "$METADATA_SERVICE_GCS_CREDENTIALS"; then
  echo "METADATA_SERVICE_GCS_CREDENTIALS environment variable must be set" >&2
  exit 1
fi
if ! test "$GCS_CREDENTIALS"; then
  echo "GCS_CREDENTIALS environment variable must be set" >&2
  exit 1
fi

spec_cache_bucket="dev-airbyte-cloud-connector-metadata-service"
metadata_bucket="dev-airbyte-cloud-connector-metadata-service"

syft_docker_image="anchore/syft:v1.6.0"
sbom_extension="spdx.json"

meta="${CONNECTORS_DIR}/${connector}/metadata.yaml"
doc="$(connector_docs_path $connector)"

docker_repository=$(yq -r '.data.dockerRepository' "$meta")
if test -z "$docker_repository" || test "$docker_repository" = "null"; then
  echo "Error: docker_repository missing in ${meta}" >&2
  exit 1
fi

# Figure out the tag that we're working on (i.e. handle the prerelease case)
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

full_docker_image="$docker_repository:$docker_tag"

# Upload the specs to the spec cache
run_connector_spec() {
  local deployment_mode=$1
  local output_file=$2

  # Run the spec command, filter for SPEC messages, and write those messages to the output file.
  # The jq command has a lot going on:
  # * --raw-input is needed, because many connectors emit some log messages in non-JSON format
  # * then we use `fromjson?` to filter for valid JSON messages
  # * and then we select any spec message (i.e. {"type": "SPEC", "spec": {...}})
  # * and then we extract just the `spec` field.
  docker run --env DEPLOYMENT_MODE=$deployment_mode "$full_docker_image" spec | jq --raw-input --compact-output 'fromjson? | select(.type == "SPEC").spec' > $output_file

  # Verify that we had exactly one spec message.
  # Depending on the platform, `wc -l` may return a right-padded string like "   1".
  # `tr -d ' '` deletes those spaces.
  local specMessageCount=$(cat $output_file | wc -l | tr -d ' ')
  if test $specMessageCount -ne 1; then
    echo "Expected to get exactly one spec message from the connector when running with deployment mode '$deployment_mode'; got $specMessageCount" >&2
    exit 1
  fi
}
echo '--- UPLOADING SPEC TO SPEC CACHE ---'
echo 'Running spec for OSS...'
run_connector_spec OSS spec.json
echo 'Running spec for CLOUD...'
run_connector_spec CLOUD spec.cloud.json
spec_cache_base_path="gs://$spec_cache_bucket/specs/$docker_repository/$docker_tag"
gcloud_activate_service_account "$SPEC_CACHE_GCS_CREDENTIALS"
gsutil cp spec.json "$spec_cache_base_path/spec.json"
# Only upload spec.cloud.json if it's different from spec.json.
# somewhat confusingly - `diff` returns true if the files are _identical_, so we need `! diff`.
if ! diff spec.json spec.cloud.json; then
  gsutil cp spec.cloud.json "$spec_cache_base_path/spec.cloud.json"
fi

# Upload the SBOM
echo '--- UPLOADING SBOM ---'
docker run \
  --volume $HOME/.docker/config.json:/config/config.json \
  --env DOCKER_CONFIG=/config \
  "$syft_docker_image" \
  -o spdx-json \
  "$full_docker_image" > "$sbom_extension"
gcloud_activate_service_account "$METADATA_SERVICE_GCS_CREDENTIALS"
gsutil cp "$sbom_extension" "gs://$metadata_bucket/sbom/$docker_repository/$docker_tag.$sbom_extension"

# Upload the metadata
# `metadata_service upload` skips the upload if the metadata already exists in GCS.
echo '--- UPLOADING METADATA ---'
if test "$publish_mode" = "main-release"; then
  metadata_upload_prerelease_flag=''
else
  # yes, it's --prerelease and not --pre-release
  metadata_upload_prerelease_flag="--prerelease $docker_tag"
fi
# Under the hood, this reads the GCS_CREDENTIALS environment variable
poetry run --directory $METADATA_SERVICE_PATH metadata_service upload "$meta" "$DOCS_ROOT/" "$metadata_bucket" $metadata_upload_prerelease_flag

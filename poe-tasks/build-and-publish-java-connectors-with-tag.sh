#!/usr/bin/env bash
# Usage examples:
#   ./build-and-publish-java-connectors-with-tag.sh destination-dev-null source-bigquery
#   ./get-modified-connectors.sh --prev-commit | ./build-and-publish-java-connectors-with-tag.sh
set -euo pipefail

CONNECTORS_DIR="airbyte-integrations/connectors"

# ---------- helper: collect connector names ----------
collect_connectors() {
  if [ "$#" -gt 0 ]; then
    # names were passed as CLI args
    printf '%s\n' "$@"
  else
    # expect JSON on stdin from previous script
    if [ -t 0 ]; then
      echo "Error: no connector names given and no JSON piped to stdin." >&2
      exit 1
    fi
    jq -r '.connector[]'
  fi
}

# ---------- main loop ----------
build_connector() {
  local connector="$1"
  local meta_file="${CONNECTORS_DIR}/${connector}/metadata.yaml"

  if [[ ! -f "$meta_file" ]]; then
    echo "metadata.yaml not found for ${connector}" >&2
    exit 1
  fi

  local image_tag
  image_tag=$(yq -r '.data.dockerImageTag' "$meta_file")

  if [[ -z "$image_tag" || "$image_tag" == "null" ]]; then
    echo "dockerImageTag missing in ${meta_file}" >&2
    exit 1
  fi

  echo "🔨  Building ${connector} with tag ${image_tag}"
  ./gradlew -Pdocker.publish \
            -DciMode=true \
            -Pdocker.tag="${image_tag}" \
            ":${CONNECTORS_DIR//\//:}:${connector}:assemble"
}

collect_connectors "$@" | while read -r connector; do
  build_connector "$connector"
done

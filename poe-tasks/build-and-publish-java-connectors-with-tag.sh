#!/usr/bin/env bash
# Usage examples:
#   ./build-and-publish-java-connectors-with-tag.sh destination-dev-null source-bigquery
#   ./get-modified-connectors.sh --prev-commit | ./build-and-publish-java-connectors-with-tag.sh
set -euo pipefail

CONNECTORS_DIR="airbyte-integrations/connectors"

# ------ Defaults & arg parsing -------
publish_mode="main-release"
declare -a connectors

while [[ $# -gt 0 ]]; do
  case "$1" in
    --publish-option=*) publish_mode="${1#*=}"; shift ;;
    --publish-option)   publish_mode="$2"; shift 2 ;;
    --name=*)           connectors=("${1#*=}"); shift ;;
    --name)             connectors=("$2"); shift 2 ;;
    *)                  connectors+=("$1"); shift ;;
  esac
done

if [[ "$publish_mode" != "main-release" && "$publish_mode" != "pre-release" ]]; then
  echo "Error: Invalid --publish-option: '$publish_mode'. Use main-release or pre-release." >&2
  exit 1
fi

# ---------- helper: collect connector names ----------
get_connectors() {
  if [ "${#connectors[@]}" -gt 0 ]; then
    printf "%s\n" "${connectors[@]}"
  else
    # read JSON from stdin
    if [ -t 0 ]; then
      echo "Error:  No --name given and nothing piped to stdin." >&2
      exit 1
    fi
    jq -r '.connector[]'
  fi
}

generate_dev_tag() {
  local base="$1"
  local hash
  hash=$(git rev-parse --short HEAD)
  echo "${base}-dev.${hash}"
}

# ---------- main loop ----------
while read -r connector; do
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

  echo "🔨  Building & publishing ${connector} with tag ${docker_tag}"
#  ./gradlew -Pdocker.publish \
#            -DciMode=true \
#            -Psbom=false \
#            -Pdocker.tag="${docker_tag}" \
#            ":${CONNECTORS_DIR//\//:}:${connector}:assemble"
done < <(get_connectors)

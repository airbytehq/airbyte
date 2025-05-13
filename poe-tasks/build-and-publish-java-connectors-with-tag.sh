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
set -euo pipefail

CONNECTORS_DIR="airbyte-integrations/connectors"

# ── Rollout whitelist: only connectors listed here will be built/published
declare -A rollout_map=(
  [destination-dev-null]=1
  [destination-bigquery]=1
  [source-e2e-test]=1
  [source-postgres]=1
  [source-mysql]=1
)

# ------ Defaults & arg parsing -------
publish_mode="pre-release"
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
    --name=*)
      connectors=("${1#*=}")
      shift
      ;;
    --name)
      connectors=("$2")
      shift 2
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

# ---------- main loop ----------
while read -r connector; do
  # only publish if connector is in rollout_map
  if [[ -z ${rollout_map[$connector]:-} ]]; then
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

  echo "Building & publishing ${connector} with tag ${docker_tag}"
  ./gradlew -Pdocker.publish \
            -DciMode=true \
            -Psbom=false \
            -Pdocker.tag="${docker_tag}" \
            ":${CONNECTORS_DIR//\//:}:${connector}:assemble"
done < <(get_connectors)
echo "Done building & publishing."

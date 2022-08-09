#!/usr/bin/env bash

set -e

. tools/lib/lib.sh

function docker_tag_exists() {
  # Added check for images pushed to github container registry
  if [[ $1 == ghcr* ]]
  then
    TOKEN_URL=https://ghcr.io/token\?scope\="repository:$1:pull"
    token=$(curl $TOKEN_URL | jq -r '.token')
    URL=https://ghcr.io/v2/$1/manifests/$2
    printf "\tURL: %s\n" "$URL"
    curl --silent -H "Authorization: Bearer $token" -f -lSL "$URL" > /dev/null
  else
    URL=https://hub.docker.com/v2/repositories/"$1"/tags/"$2"
    printf "\tURL: %s\n" "$URL"
    curl --silent -f -lSL "$URL" > /dev/null
  fi
}

checkPlatformImages() {
  echo "Checking platform images exist..."
  docker-compose pull || exit 1
  echo "Success! All platform images exist!"
}

checkNormalizationImages() {
  # the only way to know what version of normalization the platform is using is looking in NormalizationRunnerFactory.
  local image_version;
  image_version=$(cat airbyte-workers/src/main/java/io/airbyte/workers/normalization/NormalizationRunnerFactory.java | grep 'NORMALIZATION_VERSION =' | cut -d"=" -f2 | sed 's:;::' | sed -e 's:"::g' | sed -e 's:[[:space:]]::g')
  echo "Checking normalization images with version $image_version exist..."
  VERSION=$image_version docker-compose -f airbyte-integrations/bases/base-normalization/docker-compose.yaml pull || exit 1
  echo "Success! All normalization images exist!"
}

checkConnectorImages() {
  echo "Checking connector images exist..."

  CONNECTOR_DEFINITIONS=$(grep "dockerRepository" -h -A1 airbyte-config/init/src/main/resources/seed/*.yaml | grep -v -- "^--$" | tr -d ' ')
  [ -z "CONNECTOR_DEFINITIONS" ] && echo "ERROR: Could not find any connector definition." && exit 1

  while IFS=":" read -r _ REPO; do
      IFS=":" read -r _ TAG
      printf "${REPO}: ${TAG}\n"
      if docker_tag_exists "$REPO" "$TAG"; then
          printf "\tSTATUS: found\n"
      else
          printf "\tERROR: not found!\n" && exit 1
      fi
      # Docker hub has a rate limit of 180 requests per minute, so slow down our rate of calling the API
      # https://docs.docker.com/docker-hub/api/latest/#tag/rate-limiting
      sleep 1
  done <<< "${CONNECTOR_DEFINITIONS}"

  echo "Success! All connector images exist!"
}

main() {
  assert_root

  SUBSET=${1:-all} # default to all.
  [[ ! "$SUBSET" =~ ^(all|platform|connectors)$ ]] && echo "Usage ./tools/bin/check_image_exists.sh [all|platform|connectors]" && exit 1

  echo "checking images for: $SUBSET"

  [[ "$SUBSET" =~ ^(all|platform)$ ]] && checkPlatformImages
  [[ "$SUBSET" =~ ^(all|platform|connectors)$ ]] && checkNormalizationImages
  [[ "$SUBSET" =~ ^(all|connectors)$ ]] && checkConnectorImages

  echo "Image check complete."
}

main "$@"

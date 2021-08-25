#!/usr/bin/env bash

set -e

. tools/lib/lib.sh

function docker_tag_exists() {
    URL=https://hub.docker.com/v2/repositories/"$1"/tags/"$2"
    printf "\tURL: %s\n" "$URL"
    curl --silent -f -lSL "$URL" > /dev/null
}

checkPlatformImages() {
  echo "Checking platform images exist..."
  docker-compose pull || exit 1
  echo "Success! All platform images exist!"
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
  done <<< "${CONNECTOR_DEFINITIONS}"

  echo "Success! All connector images exist!"
}

main() {
  assert_root

  SUBSET=${1:-all} # default to all.
  [[ ! "$SUBSET" =~ ^(all|platform|connectors)$ ]] && echo "Usage ./tools/bin/check_image_exists.sh [all|platform|connectors]" && exit 1

  echo "checking images for: $SUBSET"

  [[ "$SUBSET" =~ ^(all|platform)$ ]] && checkPlatformImages
  [[ "$SUBSET" =~ ^(all|connectors)$ ]] && checkConnectorImages

  echo "Image check complete."
}

main "$@"

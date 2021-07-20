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

  CONFIG_FILES=$(find airbyte-config/init | grep json | grep -v STANDARD_WORKSPACE | grep -v build)
  [ -z "$CONFIG_FILES" ] && echo "ERROR: Could not find any config files." && exit 1

  while IFS= read -r file; do
      REPO=$(jq -r .dockerRepository < "$file")
      TAG=$(jq -r .dockerImageTag < "$file")
      echo "Checking $file..."
      printf "\tREPO: %s\n" "$REPO"
      printf "\tTAG: %s\n" "$TAG"
      if docker_tag_exists "$REPO" "$TAG"; then
          printf "\tSTATUS: found\n"
      else
          printf "\tERROR: not found!\n" && exit 1
      fi
  done <<< "$CONFIG_FILES"

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

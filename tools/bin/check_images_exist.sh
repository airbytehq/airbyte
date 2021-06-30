#!/usr/bin/env bash

set -e

function docker_tag_exists() {
    URL=https://hub.docker.com/v2/repositories/"$1"/tags/"$2"
    printf "\tURL: %s\n" "$URL"
    curl --silent -f -lSL "$URL" > /dev/null
}

echo "Checking core images exist..."
docker-compose pull || exit 1

echo "Checking integration images exist..."
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

echo "Success! All images exist!"

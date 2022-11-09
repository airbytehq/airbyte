#! /bin/bash

set -ex

SCRIPT_DIR="$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"

if ! command -v timeout &> /dev/null
then
    echo "timeout could not be found, installing it"
    brew install coreutils
fi

NEW_HASH="$( git rev-parse HEAD )"

git checkout master
git pull --no-rebase

SUB_BUILD=PLATFORM "$SCRIPT_DIR"/../../gradlew -p "$SCRIPT_DIR"/../.. generate-docker

cd "$SCRIPT_DIR"/../..
VERSION=dev docker compose -f "$SCRIPT_DIR"/../../docker-compose.yaml up &

sleep 75
VERSION=dev docker compose down

git stash
git checkout $NEW_HASH
SUB_BUILD=PLATFORM "$SCRIPT_DIR"/../../gradlew -p "$SCRIPT_DIR"/../.. generate-docker

VERSION=dev docker compose -f "$SCRIPT_DIR"/../../docker-compose.yaml up

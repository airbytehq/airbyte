#! /bin/bash

set -ex

SCRIPT_DIR="$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"

if ! command -v timeout &> /dev/null
then
    echo "timeout could not be found, installing it"
    brew install timeout
fi

NEW_HASH="$( git rev-parse HEAD )"

git checkout master
git pull --no-rebase

SUB_BUILD=PLATFORM "$SCRIPT_DIR"/../../gradlew -p "$SCRIPT_DIR"/../.. generate-docker

VERSION=dev timeout -k 120s 60s docker-compose -f "$SCRIPT_DIR"/../../docker-compose.yaml up &
pid=$!
wait pid

git stash
git checkout $NEW_HASH
SUB_BUILD=PLATFORM "$SCRIPT_DIR"/../../gradlew -p "$SCRIPT_DIR"/../.. generate-docker

VERSION=dev docker-compose -f "$SCRIPT_DIR"/../../docker-compose.yaml up

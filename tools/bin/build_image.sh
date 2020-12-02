#!/usr/bin/env bash

set -e

ROOT_DIR="$1"
PROJECT_DIR="$2"
DOCKERFILE="$3"
TAGGED_IMAGE="$4"
ID_FILE="$5"

cd "$ROOT_DIR"
. tools/lib/lib.sh
assert_root

cd "$PROJECT_DIR"

docker build \
  -f "$DOCKERFILE" . \
  -t "$TAGGED_IMAGE" \
  --iidfile "$ID_FILE"

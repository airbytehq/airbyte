#!/usr/bin/env bash

set -e

RESOLVED_PATH=kube/docker-compose-resolved.yaml

docker-compose config > "$RESOLVED_PATH"
docker run --rm --name kompose -it -v "$(pwd)":/src femtopixel/kompose convert -f "$RESOLVED_PATH" -o kube/local

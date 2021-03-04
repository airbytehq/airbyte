#!/usr/bin/env bash

set -e

. tools/lib/lib.sh

echo "Disk space before:"
docker run --rm busybox df -h

docker images "airbyte/source*" | grep airbyte | grep -v postgres | tr -s ' ' | cut -d" " -f 3 | xargs -n 1 -I {} docker image rm {}
docker images "airbyte/destination*" | grep airbyte | grep -v postgres | tr -s ' ' | cut -d" " -f 3 | xargs -n 1 -I {} docker image rm {}
docker image prune --force

echo "Disk space after:"
docker run --rm busybox df -h

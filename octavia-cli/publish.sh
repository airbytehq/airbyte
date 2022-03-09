#!/usr/bin/env bash

set -eux
VERSION=$1
docker tag airbyte/octavia-cli:dev airbyte/octavia-cli:${VERSION}
docker push airbyte/octavia-cli:${VERSION}

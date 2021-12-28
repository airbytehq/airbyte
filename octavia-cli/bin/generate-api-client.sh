#!/usr/bin/env bash

set -e

[ -z "$ROOT_DIR" ] && exit 1

OPENAPI_CONFIG_PATH=airbyte-api/src/main/openapi/config.yaml
GENERATED_CLIENT_PATH=octavia-cli/airbyte_api_client

function main() {
  rm -rf "$ROOT_DIR/$GENERATED_CLIENT_PATH"/*.py

  docker run --user "$(id -u):$(id -g)" -v "$ROOT_DIR":/airbyte openapitools/openapi-generator-cli generate \
    -i "/airbyte/$OPENAPI_CONFIG_PATH" \
    -o "/airbyte/$GENERATED_CLIENT_PATH" \
    -g python \
    --additional-properties=packageName=airbyte_api_client
}

main "$@"

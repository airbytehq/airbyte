##!/usr/bin/env sh

# we need to patch this variable as the docker image does not match the directory name
ROOT_DIR="$(git rev-parse --show-toplevel)"
CONNECTOR_DIR="$ROOT_DIR/airbyte-integrations/connectors/source-planetscale"

source "$(git rev-parse --show-toplevel)/airbyte-integrations/bases/connector-acceptance-test/acceptance-test-docker.sh"

#!/usr/bin/env sh

set -e

ROOT_DIR="$(git rev-parse --show-toplevel)"
CONFIG_PATH="$(readlink -f acceptance-test-config.yml)"

LOCAL_CDK="$LOCAL_CDK" CONFIG_PATH="$CONFIG_PATH" "$ROOT_DIR/airbyte-integrations/bases/connector-acceptance-test/acceptance-test-docker.sh"

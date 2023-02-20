#!/usr/bin/env sh

set -e

ROOT_DIR="$(git rev-parse --show-toplevel)"
source "$ROOT_DIR/airbyte-integrations/scripts/utils.sh"

CONFIG_PATH="$(readlink_f acceptance-test-config.yml)"
LOCAL_CDK="$LOCAL_CDK" FETCH_SECRETS="$FETCH_SECRETS" CONFIG_PATH="$CONFIG_PATH" "$ROOT_DIR/airbyte-integrations/bases/connector-acceptance-test/acceptance-test-docker.sh"

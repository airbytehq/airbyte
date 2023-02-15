#!/usr/bin/env sh

set -e

[ -n "$CONFIG_PATH" ] || die "Missing CONFIG_PATH"

ROOT_DIR="$(git rev-parse --show-toplevel)"

source "$ROOT_DIR/airbyte-integrations/bases/connectors/utils.sh"

CONNECTOR_TAG_BASE="$(grep connector_image $CONFIG_PATH | head -n 1 | cut -d: -f2 | sed 's/^ *//')"
CONNECTOR_TAG="$CONNECTOR_TAG_BASE:dev"
CONNECTOR_NAME="$(echo $CONNECTOR_TAG_BASE | cut -d / -f 2)"
CONNECTOR_DIR="$ROOT_DIR/airbyte-integrations/connectors/$CONNECTOR_NAME"

if [ -n "$FETCH_SECRETS" ]; then
  cd $ROOT_DIR
  VERSION=dev $ROOT_DIR/tools/.venv/bin/ci_credentials $CONNECTOR_NAME write-to-storage || true
  cd -
fi

if [ -n "$LOCAL_CDK" ] && [ -f "$CONNECTOR_DIR/setup.py" ]; then
  echo "Building Connector image with local CDK from $ROOT_DIR/airbyte-cdk"
  CONNECTOR_NAME="$CONNECTOR_NAME" CONNECTOR_TAG="$CONNECTOR_TAG" sh "$ROOT_DIR/airbyte-integrations/bases/connectors/build-connector-image-with-local-cdk.sh"
else
  # Build latest connector image
  docker_build_quiet "$CONNECTOR_TAG"
fi

# Pull latest acctest image
docker pull airbyte/connector-acceptance-test:latest

# Run
docker run --rm \
    -v /var/run/docker.sock:/var/run/docker.sock \
    -v /tmp:/tmp \
    -v "$CONNECTOR_DIR":/test_input \
    airbyte/connector-acceptance-test \
    --acceptance-test-config /test_input


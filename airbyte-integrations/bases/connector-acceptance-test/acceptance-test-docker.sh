#!/usr/bin/env sh

set -e

ROOT_DIR="$(git rev-parse --show-toplevel)"
source "$ROOT_DIR/airbyte-integrations/scripts/utils.sh"

CONFIG_PATH="$(readlink_f acceptance-test-config.yml)"

[ -n "$CONFIG_PATH" ] || die "Missing CONFIG_PATH"

CONNECTOR_TAG_BASE="$(grep connector_image $CONFIG_PATH | head -n 1 | cut -d: -f2 | sed 's/^ *//')"
CONNECTOR_TAG="$CONNECTOR_TAG_BASE:dev"
CONNECTOR_NAME="$(echo $CONNECTOR_TAG_BASE | cut -d / -f 2)"
CONNECTOR_DIR="$ROOT_DIR/airbyte-integrations/connectors/$CONNECTOR_NAME"

if [ -n "$FETCH_SECRETS" ]; then
  cd $ROOT_DIR
  pip install pipx
  pipx ensurepath
  pipx install airbyte-ci/connectors/ci_credentials
  VERSION=dev ci_credentials $CONNECTOR_NAME write-to-storage || true
  cd -
fi

if [ -n "$LOCAL_CDK" ] && [ -f "$CONNECTOR_DIR/setup.py" ]; then
  echo "Building Connector image with local CDK from $ROOT_DIR/airbyte-cdk"
  echo "Building docker image $CONNECTOR_TAG."
  CONNECTOR_NAME="$CONNECTOR_NAME" CONNECTOR_TAG="$CONNECTOR_TAG" QUIET_BUILD="$QUIET_BUILD" sh "$ROOT_DIR/airbyte-integrations/scripts/build-connector-image-with-local-cdk.sh"
else
  # Build latest connector image
  docker build -t "$CONNECTOR_TAG" .
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


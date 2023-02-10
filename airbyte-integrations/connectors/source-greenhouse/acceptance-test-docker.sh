#!/usr/bin/env sh

set -e

ROOT_DIR="$(git rev-parse --show-toplevel)"
CDK_DIR="$ROOT_DIR/airbyte-cdk/python"
CONNECTOR_TAG="$(grep connector_image acceptance-test-config.yml | head -n 1 | cut -d: -f2 | sed 's/^ *//')"
CONNECTOR_NAME="$(echo $CONNECTOR_TAG | cut -d / -f 2)"
CONNECTOR_DIR="$ROOT_DIR/airbyte-integrations/connectors/$CONNECTOR_NAME"
CONNECTOR_SUBDIR="$CONNECTOR_DIR/$(echo $CONNECTOR_NAME | sed 's/-/_/g')"
BUILD_DIR=$(mktemp -d)

if [ -n "$LOCAL_CDK" ]; then
  # Copy the CDK & connector files to the build directory
  cd "$BUILD_DIR"
  cp $CONNECTOR_DIR/setup.py .
  cp $CONNECTOR_DIR/main.py .
  cp $CONNECTOR_DIR/Dockerfile .
  cp -r $CONNECTOR_SUBDIR .
  cp -r $CONNECTOR_DIR/secrets .
  cp -r "$CDK_DIR" airbyte-cdk

  # Insert an instruction to the Dockerfile to copy the local CDK
  awk 'NR==1 {print; print "COPY airbyte-cdk /airbyte-cdk"} NR!=1' Dockerfile > Dockerfile.copy
  mv Dockerfile.copy Dockerfile

  # Modify setup.py so it uses the local CDK
  sed -iE 's,"airbyte-cdk[^"]*","airbyte-cdk @ file://localhost/airbyte-cdk",' setup.py

  # Build the connector image
  docker build . -t "$CONNECTOR_TAG:dev"
  cd -

  # Clean up now that the image has been created
  rm -rf "$BUILD_DIR"
else
  # Build latest connector image
  docker build . -t "$CONNECTOR_TAG:dev"
fi

# Pull latest acctest image
docker pull airbyte/connector-acceptance-test:latest

# Run
docker run --rm -it \
    -v /var/run/docker.sock:/var/run/docker.sock \
    -v /tmp:/tmp \
    -v "$CONNECTOR_DIR":/test_input \
    airbyte/connector-acceptance-test \
    --acceptance-test-config /test_input


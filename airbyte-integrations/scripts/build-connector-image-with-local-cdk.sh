#!/usr/bin/env bash

set -e

ROOT_DIR="$(git rev-parse --show-toplevel)"
source "$ROOT_DIR/airbyte-integrations/scripts/utils.sh"

[ -n "$CONNECTOR_TAG" ] || die "Missing CONNECTOR_TAG"
[ -n "$CONNECTOR_NAME" ] || die "Missing CONNECTOR_NAME"

echo "Building docker image for $CONNECTOR_NAME with local CDK"

CDK_DIR="$ROOT_DIR/airbyte-cdk/python"
CONNECTOR_DIR="$ROOT_DIR/airbyte-integrations/connectors/$CONNECTOR_NAME"
CONNECTOR_SUBDIR="$CONNECTOR_DIR/$(echo $CONNECTOR_NAME | sed 's/-/_/g')"
BUILD_DIR=$(mktemp -d)

# Copy the connector files & CDK to the build directory
cd "$BUILD_DIR"
cp "$CONNECTOR_DIR/setup.py" .
cp "$CONNECTOR_DIR/main.py" .
cp "$CONNECTOR_DIR/Dockerfile" .
cp -r "$CONNECTOR_SUBDIR" .
mkdir airbyte-cdk
rsync -a --exclude "build/" --exclude ".venv/" "$CDK_DIR/" airbyte-cdk/

# Insert an instruction to the Dockerfile to copy the local CDK
awk 'NR==1 {print; print "COPY airbyte-cdk /airbyte-cdk"} NR!=1' Dockerfile > Dockerfile.copy
mv Dockerfile.copy Dockerfile

# Modify setup.py so it uses the local CDK
sed -iE 's,"airbyte-cdk[^"]*","airbyte-cdk @ file://localhost/airbyte-cdk",' setup.py

# Build the connector image
if [ -n "$QUIET_BUILD" ]; then
  docker build -t "$CONNECTOR_TAG" -q .
else
  docker build -t "$CONNECTOR_TAG" .
fi

cd -

# Clean up now that the image has been created
rm -rf "$BUILD_DIR"

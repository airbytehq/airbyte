#!/usr/bin/env sh

set -e

[ -n "$CONNECTOR_TAG" ] || die "Missing CONNECTOR_TAG"
[ -n "$CONNECTOR_NAME" ] || die "Missing CONNECTOR_NAME"

ROOT_DIR="$(git rev-parse --show-toplevel)"

source "$ROOT_DIR/airbyte-integrations/bases/connectors/utils.sh"

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
cp -r "$CDK_DIR" airbyte-cdk

# Insert an instruction to the Dockerfile to copy the local CDK
awk 'NR==1 {print; print "COPY airbyte-cdk /airbyte-cdk"} NR!=1' Dockerfile > Dockerfile.copy
mv Dockerfile.copy Dockerfile

# Modify setup.py so it uses the local CDK
sed -iE 's,"airbyte-cdk[^"]*","airbyte-cdk @ file://localhost/airbyte-cdk",' setup.py

# Build the connector image
docker_build_quiet "$CONNECTOR_TAG"
cd -

# Clean up now that the image has been created
rm -rf "$BUILD_DIR"

#!/usr/bin/env sh

CONNECTOR_NAME=$1
OUTPUT_DIR=$2

ROOT_DIR="$(git rev-parse --show-toplevel)"
source "$ROOT_DIR/airbyte-integrations/scripts/utils.sh"

[ -n "$CONNECTOR_NAME" ] || die "Missing CONNECTOR_NAME"
[ -n "$OUTPUT_DIR" ] || die "Missing OUTPUT_DIR"

CONNECTOR_DIR=$ROOT_DIR/airbyte-integrations/connectors/$CONNECTOR_NAME
CONNECTOR_OUTPUT_DIR=$OUTPUT_DIR/$CONNECTOR_NAME

cd $CONNECTOR_DIR

if [ -f acceptance-test-docker.sh ] && [ -f setup.py ] && grep -q "airbyte-cdk" setup.py; then
    mkdir $CONNECTOR_OUTPUT_DIR
    echo "Building docker image for $CONNECTOR_NAME."
    LOCAL_CDK=1 FETCH_SECRETS=1 QUIET_BUILD=1 sh acceptance-test-docker.sh > $CONNECTOR_OUTPUT_DIR/$CONNECTOR_NAME.out 2> $CONNECTOR_OUTPUT_DIR/$CONNECTOR_NAME.err
    echo $? > $CONNECTOR_OUTPUT_DIR/$CONNECTOR_NAME.exit-code
fi

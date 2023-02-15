#!/usr/bin/env sh

ROOT_DIR="$(git rev-parse --show-toplevel)"
OUTPUT_DIR=/tmp/cat-output
SCRIPT=/tmp/run-cats-with-local-cdk.sh
# Clean up from previous test runs
rm -rf $OUTPUT_DIR && mkdir $OUTPUT_DIR

while getopts ":c:" opt; do
    case $opt in
        c ) connectors="${OPTARG}" ;;
        * ) exit 1
    esac
done

if [ -z "$connectors" ]; then
  connectors=$(find airbyte-integrations/connectors -type d -name 'source-*' -maxdepth 1 | xargs -n 1 basename | tr '\n' ',' | sed 's/,$//')
fi

connectors=$(echo $connectors | tr ',' ' ')

echo "Running CATs"
echo ""

echo '
CONNECTOR_NAME=$1
ROOT_DIR="$(git rev-parse --show-toplevel)"
CONNECTOR_DIR=$ROOT_DIR/airbyte-integrations/connectors/$CONNECTOR_NAME
OUTPUT_DIR=/tmp/cat-output
CONNECTOR_OUTPUT_DIR=$OUTPUT_DIR/$CONNECTOR_NAME
if [ -f $CONNECTOR_DIR/acceptance-test-docker.sh ] && [ -f $CONNECTOR_DIR/setup.py ] && grep -q "airbyte-cdk" $CONNECTOR_DIR/setup.py; then
    mkdir $CONNECTOR_OUTPUT_DIR
    VERSION=dev $ROOT_DIR/tools/.venv/bin/ci_credentials $CONNECTOR_NAME write-to-storage > /dev/null 2> $CONNECTOR_OUTPUT_DIR/$CONNECTOR_NAME.err
    cd $CONNECTOR_DIR
    LOCAL_CDK=1 sh acceptance-test-docker.sh > $CONNECTOR_OUTPUT_DIR/$CONNECTOR_NAME.out 2> $CONNECTOR_OUTPUT_DIR/$CONNECTOR_NAME.err
    echo $? > $CONNECTOR_OUTPUT_DIR/$CONNECTOR_NAME.exit-code
fi
' > "$SCRIPT"

chmod +x "$SCRIPT"

echo $connectors | xargs -P 0 -n 1 -I % "$SCRIPT" %

# Print connectors with CATs that passed
for directory in $OUTPUT_DIR/*; do
  SOURCE_NAME="$(basename $directory)"
  CONNECTOR_OUTPUT_LOC="$OUTPUT_DIR/$SOURCE_NAME/$SOURCE_NAME"
  if [ "$(cat $CONNECTOR_OUTPUT_LOC.exit-code)" = 0 ]; then
    echo "$SOURCE_NAME: ok"
  fi
done

echo ""

# Print errors
for directory in $OUTPUT_DIR/*; do
  SOURCE_NAME="$(basename $directory)"
  CONNECTOR_OUTPUT_LOC="$OUTPUT_DIR/$SOURCE_NAME/$SOURCE_NAME"
  if [ "$(cat $CONNECTOR_OUTPUT_LOC.exit-code)" != 0 ]; then
    echo "$SOURCE_NAME errors:"
    echo "$(cat $CONNECTOR_OUTPUT_LOC.out)"
    echo "$(cat $CONNECTOR_OUTPUT_LOC.err)"
    echo ""
  fi
done

rm "$SCRIPT"

echo "Done."

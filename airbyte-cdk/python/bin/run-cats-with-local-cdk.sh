#!/usr/bin/env sh

ROOT_DIR="$(git rev-parse --show-toplevel)"

REPO_NAME="$(basename $ROOT_DIR)"
if [ "$REPO_NAME" != "airbyte" ]; then
  echo "This script must be run from the airbyte repo." 1>&2
  exit 1
fi

source "$ROOT_DIR/airbyte-integrations/scripts/utils.sh"

USAGE="$(basename "$0") [-h] [-c connector1,connector2,...] -- Run connector acceptance tests (CATs) against the local CDK, if relevant.\n
    -h  show help text\n
    -c  comma-separated connector names (defaults to all connectors)"

OUTPUT_DIR=/tmp/cat-output
SCRIPT=/tmp/run-cats-with-local-cdk.sh
# Clean up from previous test runs
rm -rf $OUTPUT_DIR && mkdir $OUTPUT_DIR

while getopts ":hc:" opt; do
    case $opt in
        h ) echo $USAGE
            exit 0 ;;
        c ) connectors="${OPTARG}" ;;
        * ) die "Unrecognized argument" ;;
    esac
done

[ -n "$connectors" ] || die "Please specify one or more connectors."

connectors=$(echo $connectors | tr ',' ' ')

echo "Running CATs for ${connectors}"
echo ""
echo $connectors | xargs -P 0 -n 1 -I % $ROOT_DIR/airbyte-integrations/scripts/run-acceptance-test-docker.sh % $OUTPUT_DIR

# Print connectors with CATs that passed
for directory in $OUTPUT_DIR/*; do
  SOURCE_NAME="$(basename $directory)"
  CONNECTOR_OUTPUT_LOC="$OUTPUT_DIR/$SOURCE_NAME/$SOURCE_NAME"
  if [ "$(cat $CONNECTOR_OUTPUT_LOC.exit-code)" = 0 ]; then
    echo "$SOURCE_NAME: CATs ran successfully!"
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

echo "Done."

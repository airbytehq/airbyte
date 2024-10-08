#!/bin/bash
# Intentionally no set -e, because we want to run normalization even if the destination fails
set -o pipefail

/airbyte/base.sh $@
destination_exit_code=$?
echo '{"type": "LOG","log":{"level":"INFO","message":"Destination process done (exit code '"$destination_exit_code"')"}}'

# store original args
args=$@

while [ $# -ne 0 ]; do
  case "$1" in
  --config)
    CONFIG_FILE="$2"
    shift 2
    ;;
  *)
    # move on
    shift
    ;;
  esac
done

# restore original args after shifts
set -- $args

USE_1S1T_FORMAT="false"
if [[ -s "$CONFIG_FILE" ]]; then
  USE_1S1T_FORMAT=$(jq -r '.use_1s1t_format' "$CONFIG_FILE")
fi

if test "$1" != 'write'
then
  normalization_exit_code=0
elif test "$NORMALIZATION_TECHNIQUE" = 'LEGACY' && test "$USE_1S1T_FORMAT" != "true"
then
  echo '{"type": "LOG","log":{"level":"INFO","message":"Starting in-connector normalization"}}'
  # Normalization tries to create this file from the connector config and crashes if it already exists
  # so just nuke it and let normalization recreate it.
  # Use -f to avoid error if it doesn't exist, since it's only created for certain SSL modes.
  rm -f ca.crt
  # the args in a write command are `write --catalog foo.json --config bar.json`
  # so if we remove the `write`, we can just pass the rest directly into normalization
  /airbyte/entrypoint.sh run ${@:2} --integration-type $AIRBYTE_NORMALIZATION_INTEGRATION | java -cp "/airbyte/lib/*" io.airbyte.cdk.integrations.destination.normalization.NormalizationLogParser
  normalization_exit_code=$?
  echo '{"type": "LOG","log":{"level":"INFO","message":"In-connector normalization done (exit code '"$normalization_exit_code"')"}}'
else
  echo '{"type": "LOG","log":{"level":"INFO","message":"Skipping in-connector normalization"}}'
  normalization_exit_code=0
fi

if test $destination_exit_code -ne 0
then
  exit $destination_exit_code
elif test $normalization_exit_code -ne 0
then
  exit $normalization_exit_code
else
  exit 0
fi

#!/bin/bash
# Intentionally no set -e, because we want to run normalization even if the destination fails
set -o pipefail

/airbyte/base.sh $@
destination_exit_code=$?
echo '{"type": "LOG","log":{"level":"INFO","message":"Destination process done (exit code '"$destination_exit_code"')"}}'
echo '{"type": "LOG","log":{"level":"INFO","message":"This container no longer runs normalization"}}'

exit 0

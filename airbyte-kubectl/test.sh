#!/bin/bash

set -o pipefail -ue

NAME="airbyte-kubectl-test"

echo "Testing airbyte kubectl..."

docker run --rm airbyte/kubectl:${VERSION-dev} version --output yaml --client=true
# Check that bash works, and so does date (needs coreutils ver)
docker run --rm --entrypoint bash airbyte/kubectl:${VERSION-dev} -c date -d 'now - 2 hours'

echo "Tests Passed ✅"
exit 0

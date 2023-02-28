#!/usr/bin/env bash

set -e

. tools/lib/lib.sh

# build & runs docker scan for an integration name
# run from the root of the monorepo
# utilization like `./tools/bin/ci_docker_scan.sh source-github`

connector="$1"
tag="dev"
severity="medium"

if [[ "$connector" == *"base-normalization"* ]]; then
  echo "Skipping base scan..."
  exit 0
elif [[ "$connector" == *"source-acceptance-test"* ]]; then
  buildCommand="$(_to_gradle_path "airbyte-integrations/bases/$connector_name" build)"
  export SUB_BUILD="CONNECTORS_BASE"
elif [[ "$connector" == *"bases"* ]]; then
  echo "Skipping base scan..."
  exit 0
elif [[ "$connector" == *"connectors"* ]]; then
  buildCommand="$(_to_gradle_path "airbyte-integrations/$connector" build)"
else
  buildCommand=":airbyte-integrations:connectors:$connector:build"
fi

if [ -n "$buildCommand" ] ; then
  echo "----- Building $connector Container -----"
  echo "Running: ./gradlew --no-daemon --scan $buildCommand -x test -x _unitTestCoverage"
  ./gradlew --no-daemon --scan "$buildCommand" -x test -x _unitTestCoverage
else
  echo "Connector '$connector' not found..."
  exit 1
fi

echo "----- Starting $connector Docker Scan -----"

docker scan --accept-license --severity="$severity" "airbyte/$connector:$tag"

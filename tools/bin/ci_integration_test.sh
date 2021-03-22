#!/usr/bin/env bash

set -e

. tools/lib/lib.sh

# runs integration tests for an integration name

connector="$1"
all_integration_tests=$(./gradlew integrationTest --dry-run | grep 'integrationTest SKIPPED' | cut -d: -f 4)

if [[ "$connector" == "all" ]] ; then
  echo "Running: ./gradlew --no-daemon --scan integrationTest"
  ./gradlew --no-daemon --scan integrationTest
else
  if [[ "$connector" == *"connectors"* ]] || [[ "$connector" == *"bases"* ]]; then
    connector_name=$(echo $connector | cut -d / -f 2)
    selected_integration_test=$(echo "$all_integration_tests" | grep "^$connector_name$" || echo "")
    integrationTestCommand="$(_to_gradle_path "airbyte-integrations/$connector" integrationTest)"
  else
    selected_integration_test=$(echo "$all_integration_tests" | grep "^$connector$" || echo "")
    integrationTestCommand=":airbyte-integrations:connectors:$connector:integrationTest"
  fi
  if [ -n "$selected_integration_test" ] ; then
    echo "Running: ./gradlew --no-daemon --scan $integrationTestCommand"
    ./gradlew --no-daemon --scan "$integrationTestCommand"
  else
    echo "Connector '$connector' not found..."
    exit 1
  fi
fi

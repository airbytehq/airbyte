#!/usr/bin/env bash

set -e

# runs integration and/or standard tests for an integration name

connector="$1"
all_integration_tests=$(./gradlew integrationTest --dry-run | grep 'integrationTest SKIPPED' | cut -d: -f 4)
all_standard_python_tests=$(./gradlew standardSourceTestPython --dry-run | grep 'standardSourceTestPython SKIPPED' | cut -d: -f 4)

if [[ "$connector" == "all" ]] ; then
  echo "Running: ./gradlew --no-daemon --scan integrationTest standardSourceTestPython"
  ./gradlew --no-daemon --scan integrationTest standardSourceTestPython
else
  selected_integration_test=$(echo "$all_integration_tests" | grep "^$connector$" || echo "")
  selected_standard_python_test=$(echo "$all_standard_python_tests" | grep "^$connector$" || echo "")
  integrationTestCommand=":airbyte-integrations:connectors:$connector:integrationTest"
  standardPythonTestCommand=":airbyte-integrations:connectors:$connector:standardSourceTestPython"
  if [ -n "$selected_integration_test" ] && [ -n "$selected_standard_python_test" ] ; then
    echo "Running: ./gradlew --no-daemon --scan $integrationTestCommand $standardPythonTestCommand"
    ./gradlew --no-daemon --scan "$integrationTestCommand" "$standardPythonTestCommand"
  elif [ -z "$selected_integration_test" ] && [ -n "$selected_standard_python_test" ] ; then
    echo "Running: ./gradlew --no-daemon --scan $standardPythonTestCommand"
    ./gradlew --no-daemon --scan "$standardPythonTestCommand"
  elif [ -n "$selected_integration_test" ] && [ -z "$selected_standard_python_test" ] ; then
    echo "Running: ./gradlew --no-daemon --scan $integrationTestCommand"
    ./gradlew --no-daemon --scan "$integrationTestCommand"
  else
    echo "Connector '$connector' not found..."
    exit 1
  fi
fi

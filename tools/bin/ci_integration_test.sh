#!/usr/bin/env bash

set -e

# runs integration tests for an integration name

connector="$1"
all_integration_tests=$(./gradlew integrationTest --dry-run | grep 'integrationTest SKIPPED' | cut -d: -f 4)

if [[ "$connector" == "all" ]] ; then
  echo "Running: ./gradlew --no-daemon --scan integrationTest"
  ./gradlew --no-daemon --scan integrationTest
else
  STAT_KEY="$connector"-"$ACTION_RUN_ID"
  trap 'catch $? $LINENO' EXIT
  catch() {
    if [ "$GITHUB_REF" == "refs/heads/master" ]; then
      if [ "$1" == "0" ]; then
        curl "https://kvdb.io/$BUILD_STAT_BUCKET/$STAT_KEY" \
          -u "$BUILD_STAT_WRITE_KEY:" \
          -d "success-$(date +%s )"
        echo "Reported success build status."
      else
        curl "https://kvdb.io/$BUILD_STAT_BUCKET/$STAT_KEY" \
          -u "$BUILD_STAT_WRITE_KEY:" \
          -d "failure-$(date +%s )"
        echo "Reported failure build status."
      fi
    fi
  }

  if [ "$GITHUB_REF" == "refs/heads/master" ]; then
    curl "https://kvdb.io/$BUILD_STAT_BUCKET/$STAT_KEY" \
      -u "$BUILD_STAT_WRITE_KEY:" \
      -d "in_progress-$(date +%s )"
    echo "Reported in_progress build status."
  fi

  selected_integration_test=$(echo "$all_integration_tests" | grep "^$connector$" || echo "")
  integrationTestCommand=":airbyte-integrations:connectors:$connector:integrationTest"
  if [ -n "$selected_integration_test" ] ; then
    echo "Running: ./gradlew --no-daemon --scan $integrationTestCommand"
    ./gradlew --no-daemon --scan "$integrationTestCommand"
  else
    echo "Connector '$connector' not found..."
    exit 1
  fi
fi

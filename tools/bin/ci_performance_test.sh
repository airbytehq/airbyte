#!/usr/bin/env bash

set -e

. tools/lib/lib.sh

# runs performance tests for an performance name

connector="$1"
if [[ "$2" ]]; then
  if [[ "$2" == *"cpulimit"* ]]; then
    firstarg="-DcpuLimit=$(echo $2 | cut -d / -f 2)"
  fi
  if [[ "$2" == *"memorylimit"* ]]; then
    firstarg="-DmemoryLimit=$(echo $2 | cut -d / -f 2)"
  fi
fi
if [[ "$3" ]]; then
  if [[ "$3" == *"cpulimit"* ]]; then
    secondarg="-DcpuLimit=$(echo $3 | cut -d / -f 2)"
  fi
  if [[ "$3" == *"memorylimit"* ]]; then
    secondarg="-DmemoryLimit=$(echo $3 | cut -d / -f 2)"
  fi
fi
all_performance_tests=$(./gradlew performanceTest --dry-run | grep 'performanceTest SKIPPED' | cut -d: -f 4)
run() {
if [[ "$connector" == "all" ]] ; then
  echo "Running: ./gradlew --no-daemon --scan performanceTest"
  ./gradlew --no-daemon --scan performanceTest
else
  if [[ "$connector" == *"base-normalization"* ]]; then
    selected_performance_test="base-normalization"
    performanceTestCommand="$(_to_gradle_path "airbyte-integrations/bases/base-normalization" performanceTest)"
    export SUB_BUILD="CONNECTORS_BASE"
    # avoid schema conflicts when multiple tests for normalization are run concurrently
    export RANDOM_TEST_SCHEMA="true"
    ./gradlew --no-daemon --scan airbyteDocker
  elif [[ "$connector" == *"bases"* ]]; then
    connector_name=$(echo $connector | cut -d / -f 2)
    selected_performance_test=$(echo "$all_performance_tests" | grep "^$connector_name$" || echo "")
    performanceTestCommand="$(_to_gradle_path "airbyte-integrations/$connector" performanceTest)"
    export SUB_BUILD="CONNECTORS_BASE"
  elif [[ "$connector" == *"connectors"* ]]; then
    connector_name=$(echo $connector | cut -d / -f 2)
    selected_performance_test=$(echo "$all_performance_tests" | grep "^$connector_name$" || echo "")
    performanceTestCommand="$(_to_gradle_path "airbyte-integrations/$connector" performanceTest)"
  else
    selected_performance_test=$(echo "$all_performance_tests" | grep "^$connector$" || echo "")
    performanceTestCommand=":airbyte-integrations:connectors:$connector:performanceTest"
  fi
  if [ -n "$selected_performance_test" ] ; then
    if [[ "$firstarg" ]]; then
      if [[ "$secondarg" ]]; then
        echo "Running: ./gradlew --no-daemon --scan $performanceTestCommand $firstarg $secondarg"
        ./gradlew --no-daemon --scan "$performanceTestCommand" "$firstarg" "$secondarg"
      else
        echo "Running: ./gradlew --no-daemon --scan $performanceTestCommand $firstarg"
        ./gradlew --no-daemon --scan "$performanceTestCommand" "$firstarg"
      fi
    else
      echo "Running: ./gradlew --no-daemon --scan $performanceTestCommand"
      ./gradlew --no-daemon --scan "$performanceTestCommand"
    fi
  else
    echo "Connector '$connector' not found..."
    return 1
  fi
fi
}

# Copy command output to extract gradle scan link.
run | tee build.out
# return status of "run" command, not "tee"
# https://tldp.org/LDP/abs/html/internalvariables.html#PIPESTATUSREF
run_status=${PIPESTATUS[0]}

test_performance $run_status == "0" || {
   # Build failed
   link=$(cat build.out | grep -a -A1 "Publishing build scan..." | tail -n1 | tr -d "\n")
   # Save gradle scan link to github GRADLE_SCAN_LINK variable for next job.
   # https://docs.github.com/en/actions/reference/workflow-commands-for-github-actions#setting-an-environment-variable
   echo "GRADLE_SCAN_LINK=$link" >> $GITHUB_ENV
   exit $run_status
}

# Build successed
coverage_report=`sed -n '/^[ \t]*-\+ coverage: /,/TOTAL   /p' build.out`

if ! test_performance -z "$coverage_report"
then
   echo "PYTHON_UNITTEST_COVERAGE_REPORT<<EOF" >> $GITHUB_ENV
   echo "Python tests coverage:" >> $GITHUB_ENV
   echo '```' >> $GITHUB_ENV
   echo "$coverage_report" >> $GITHUB_ENV
   echo '```' >> $GITHUB_ENV
   echo "EOF" >> $GITHUB_ENV
else
   echo "PYTHON_UNITTEST_COVERAGE_REPORT=No Python unittests run" >> $GITHUB_ENV
fi

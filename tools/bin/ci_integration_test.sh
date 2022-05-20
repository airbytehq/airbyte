#!/usr/bin/env bash

set -e

. tools/lib/lib.sh

# runs integration tests for an integration name

connector="$1"
all_integration_tests=$(./gradlew integrationTest --dry-run | grep 'integrationTest SKIPPED' | cut -d: -f 4)
run() {
if [[ "$connector" == "all" ]] ; then
  echo "Running: ./gradlew --no-daemon --scan integrationTest"
  SUB_BUILD=ALL_CONNECTORS ./gradlew --no-daemon --scan integrationTest
else
  if [[ "$connector" == *"base-normalization"* ]]; then
    selected_integration_test="base-normalization"
    integrationTestCommand="$(_to_gradle_path "airbyte-integrations/bases/base-normalization" integrationTest)"
    export SUB_BUILD="CONNECTORS_BASE"
    # avoid schema conflicts when multiple tests for normalization are run concurrently
    export RANDOM_TEST_SCHEMA="true"
    ./gradlew --no-daemon --scan airbyteDocker
  elif [[ "$connector" == *"bases"* ]]; then
    connector_name=$(echo $connector | cut -d / -f 2)
    selected_integration_test=$(echo "$all_integration_tests" | grep "^$connector_name$" || echo "")
    integrationTestCommand="$(_to_gradle_path "airbyte-integrations/$connector" integrationTest)"
    export SUB_BUILD="CONNECTORS_BASE"
  elif [[ "$connector" == *"connectors"* ]]; then
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
    return 1
  fi
fi
}

show_run_details() {
   echo "Run Details: $1" >> $GITHUB_STEP_SUMMARY
   run_info=`sed -n "/=* $1 =*/,/========/p" build.out`
   if ! test -z "$run_info"
   then
      echo '```' >> $GITHUB_STEP_SUMMARY
      echo "$run_info" | sed '$d' >> $GITHUB_STEP_SUMMARY  # $d removes last line
      echo '```' >> $GITHUB_STEP_SUMMARY
      echo '' >> $GITHUB_STEP_SUMMARY
   fi
}

show_skipped_failed_info() {
   echo "show_skipped_failed_info function" >> $GITHUB_STEP_SUMMARY
   skipped_failed_info=`sed -n '/=* short test summary info =*/,/========/p' build.out`
   if ! test -z "$skipped_failed_info"
      then
         echo "PYTHON_SHORT_TEST_SUMMARY_INFO<<EOF" >> $GITHUB_ENV
         echo "Python short test summary info:" >> $GITHUB_ENV
         echo '```' >> $GITHUB_ENV
         echo "$skipped_failed_info" >> $GITHUB_ENV
         echo '```' >> $GITHUB_ENV
         echo "EOF" >> $GITHUB_ENV

        echo '```' >> $GITHUB_STEP_SUMMARY
        echo "$skipped_failed_info" >> $GITHUB_STEP_SUMMARY
        echo '```' >> $GITHUB_STEP_SUMMARY
        echo '' >> $GITHUB_STEP_SUMMARY
   else
      echo "PYTHON_SHORT_TEST_SUMMARY_INFO=No skipped/failed tests"
      echo '### No skipped/failed tests' >> $GITHUB_STEP_SUMMARY
   fi
}

write_logs() {
  show_skipped_failed_info
  show_run_details 'FAILURES'
  show_run_details 'ERRORS'
}

echo 'testing GITHUB_STEP_SUMMARY'
echo "# $connector" >> $GITHUB_STEP_SUMMARY
echo "" >> $GITHUB_STEP_SUMMARY

# Copy command output to extract gradle scan link.
run | tee build.out
# return status of "run" command, not "tee"
# https://tldp.org/LDP/abs/html/internalvariables.html#PIPESTATUSREF
run_status=${PIPESTATUS[0]}

test $run_status == "0" || {
   # Build failed
   link=$(cat build.out | grep -a -A1 "Publishing build scan..." | tail -n1 | tr -d "\n")
   # Save gradle scan link to github GRADLE_SCAN_LINK variable for next job.
   # https://docs.github.com/en/actions/reference/workflow-commands-for-github-actions#setting-an-environment-variable
   echo "GRADLE_SCAN_LINK=$link" >> $GITHUB_ENV
   write_logs
   exit $run_status
}

write_logs

# Build successed
coverage_report=`sed -n '/.*Name.*Stmts.*Miss.*Cover/,/TOTAL   /p' build.out`

if ! test -z "$coverage_report"
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

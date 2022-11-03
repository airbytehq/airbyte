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
  elif [[ "$connector" == *"source-acceptance-test"* ]]; then
    connector_name=$(echo $connector | cut -d / -f 2)
    selected_integration_test="source-acceptance-test"
    integrationTestCommand="$(_to_gradle_path "airbyte-integrations/bases/$connector_name" integrationTest)"
    export SUB_BUILD="CONNECTORS_BASE"
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

show_python_run_details() {
   run_info=`sed -n "/=* $1 =*/,/========/p" build.out`
   if ! test -z "$run_info"
   then
      echo '```' >> $GITHUB_STEP_SUMMARY
      echo "$run_info" | sed '$d' >> $GITHUB_STEP_SUMMARY  # $d removes last line
      echo '```' >> $GITHUB_STEP_SUMMARY
      echo '' >> $GITHUB_STEP_SUMMARY
   fi
}

show_java_run_details() {
  # show few lines after stack trace
  run_info=`awk '/[\]\)] FAILED/{x=NR+8}(NR<=x){print}' build.out`
  if ! test -z "$run_info"
  then
    echo '```' >> $GITHUB_STEP_SUMMARY
    echo "$run_info" >> $GITHUB_STEP_SUMMARY
    echo '```' >> $GITHUB_STEP_SUMMARY
    echo '' >> $GITHUB_STEP_SUMMARY
  fi
}

write_results_summary() {
  success="$1"
  python_info=`sed -n '/=* short test summary info =*/,/========/p' build.out`
  java_info=`sed -n '/tests completed,/p' build.out` # this doesn't seem to work, not in build.out

  echo "success: $success"
  echo "python_info: $python_info"
  echo "java_info: $java_info"

  info='Could not find result summary'
  result='Unknown result'

  if [ "$success" = true ]
  then
    result="Build Passed"
    info='All Passed'
    echo '### Build Passed' >> $GITHUB_STEP_SUMMARY
    echo '' >> $GITHUB_STEP_SUMMARY
  else
    result="Build Failed"
    echo '### Build Failed' >> $GITHUB_STEP_SUMMARY
    echo '' >> $GITHUB_STEP_SUMMARY
  fi

  if ! test -z "$java_info"
  then
    info="$java_info"

    echo '```' >> $GITHUB_STEP_SUMMARY
    echo "$java_info" >> $GITHUB_STEP_SUMMARY
    echo '```' >> $GITHUB_STEP_SUMMARY
    echo '' >> $GITHUB_STEP_SUMMARY
  fi
  if ! test -z "$python_info"
  then
    info="$python_info"

    echo '```' >> $GITHUB_STEP_SUMMARY
    echo "$python_info" >> $GITHUB_STEP_SUMMARY
    echo '```' >> $GITHUB_STEP_SUMMARY
    echo '' >> $GITHUB_STEP_SUMMARY
  fi

  echo "TEST_SUMMARY_INFO<<EOF" >> $GITHUB_ENV
  echo '' >> $GITHUB_ENV
  echo "### $result" >> $GITHUB_ENV
  echo '' >> $GITHUB_ENV
  echo "Test summary info:" >> $GITHUB_ENV
  echo '```' >> $GITHUB_ENV
  echo "$info" >> $GITHUB_ENV
  echo '```' >> $GITHUB_ENV
  echo "EOF" >> $GITHUB_ENV
}

write_logs() {
  write_results_summary $1
  show_python_run_details 'FAILURES'
  show_python_run_details 'ERRORS'
  show_java_run_details
}

echo "# $connector" >> $GITHUB_STEP_SUMMARY
echo "" >> $GITHUB_STEP_SUMMARY

# Cut the $GITHUB_STEP_SUMMARY with head if its larger than 1MB
echo "$GITHUB_STEP_SUMMARY" | head -c 1048576 >> $GITHUB_STEP_SUMMARY

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
   write_logs false
   exit $run_status
}

write_logs true

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

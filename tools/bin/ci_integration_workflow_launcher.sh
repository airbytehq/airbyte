#!/usr/bin/env bash
# launches integration test workflows for master builds

# Programmer note: testing this file is easy,
# set runtime variables inline
# GITHUB_TOKEN=$YOUR_TOKEN_HERE ./ci_integration_workflow_launcher.sh

set -o errexit # -f exit for any command failure
set -o nounset # -u exit if a variable is not set
# text color escape codes (please note \033 == \e but OSX doesn't respect the \e)
blue_text='\033[94m'
red_text='\033[31m'
default_text='\033[39m'

# set -x/xtrace' uses a Sony PS4 for more info
PS4="$blue_text""$BASH_SOURCE:$LINENO   ""$default_text"
# set -o xtrace


if test -z "$GITHUB_TOKEN"; then
  echo "GITHUB_TOKEN not set..."
  exit 1
fi

repo_api=https://api.github.com/repos/airbytehq/airbyte
# workflow_path is hardcoded in a query because escaping strings is hard

# --------- Get all workflows
workflow_ids_curl_response=$(
  curl  --silent \
  --show-error \
        --header "Authorization: Bearer $GITHUB_TOKEN" \
        --request GET "$repo_api/actions/workflows"
)
echo -e "$blue_text""\$workflow_ids_curl_response is \n\n$workflow_ids_curl_response\n\n""$default_text"
echo -e "$blue_text""Running jq on \$workflow_ids_curl_response""$default_text"
echo -e "$blue_text""jq '.workflows[] | select(.path==.github/workflows/test-command.yml) | .id'""$default_text"

workflow_id=$(echo $workflow_ids_curl_response | \
    jq '.workflows[] | select(.path==".github/workflows/test-command.yml") | .id')

# We expect a unique response, 2 responses is too much
workflows_with_matching_paths=$(echo $workflow_id | wc -l)
echo -e "$blue_text""jq returned: $workflow_id""$default_text"

if test "$workflows_with_matching_paths" -ne "1" ; then
  echo -e "\n\n$red_text""Unexpected number of workflows found != 1 for .github/workflows/test-command.yml""$default_text"
  echo -e "\n\n$red_text""\$workflows_with_matching_paths = $workflows_with_matching_paths""$default_text"
  exit 1
fi

# --------- Ensure no more than 5 concurrent tests happen

max_running_master_workflows=5

running_master_workflows_curl_response=$(
  curl \
    --silent \
    --show-error \
    --header "Authorization: Bearer $GITHUB_TOKEN" \
    --request GET "$repo_api/actions/workflows/$workflow_id/runs?branch=master&status=in_progress")

echo -e "$blue_text""\$running_master_workflows_curl_response is \n\n$running_master_workflows_curl_response\n\n""$default_text"
echo -e "$blue_text""Running jq on response jq .total_count""$default_text"

running_master_workflows=$(echo "$running_master_workflows_curl_response" | jq .total_count)
echo -e "$blue_text""JQ Found \"$running_master_workflows\" running""$default_text"


if test "$running_master_workflows" -gt "$max_running_master_workflows"; then
  echo -e "$red_text""More than $max_running_master_workflows integration tests workflows running on master.""$default_text"
  echo -e "$red_text""Skipping launching workflows.  If you want this test run use manual steps!""$default_text"
  exit 0
else
  echo -e "$blue_text""Running ./gradlew integrationTest --dry-run""$default_text"
fi

# --------- Use gradle to find tests to fire

./gradlew integrationTest --dry-run
gradle_test_list_result=$?
# Tell epople if Gradle Fails
if test $gradle_test_list_result -ne 0; then
  echo -e "$red_text""Gradle FAILED to build! Try './gradlew integrationTest --dry-run' in your branch""$default_text"
else
  echo -e "$blue_text""Gradle dry run SUCCESS!""$default_text"
fi

# --------- Fire tests
connectors=$(./gradlew integrationTest --dry-run | grep 'integrationTest SKIPPED' | cut -d: -f 4 | sort | uniq)
for connector in $connectors; do
  echo -e "$blue_text""Issuing GH action request for connector $connector...""$default_text"
  curl \
    --silent \
    --show-error \
    --header "Accept: application/vnd.github.v3+json" \
    --header "Authorization: Bearer $GITHUB_TOKEN" \
    --request POST "$repo_api/actions/workflows/$workflow_id/dispatches" \
    --data "{\"ref\":\"master\", \"inputs\": { \"connector\": \"$connector\"}"
done

echo "If you are reading this the file has finished executing"

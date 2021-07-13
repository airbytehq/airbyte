#!/usr/bin/env bash

set -e

# launches integration test workflows for master builds

if [[ -z "$GITHUB_TOKEN" ]]; then
  echo "GITHUB_TOKEN not set..."
  exit 1
fi

REPO_API=https://api.github.com/repos/airbytehq/airbyte
WORKFLOW_PATH=.github/workflows/test-command.yml
WORKFLOW_ID=$(curl --header "Authorization: Bearer $GITHUB_TOKEN" "$REPO_API/actions/workflows" | jq -r ".workflows[] | select( .path == \"$WORKFLOW_PATH\" ) | .id")
MATCHING_WORKFLOW_IDS=$(wc -l <<<"${WORKFLOW_ID}")

if [ "$MATCHING_WORKFLOW_IDS" -ne "1" ]; then
  echo "More than one workflow exists with the path $WORKFLOW_PATH"
  exit 1
fi

MAX_RUNNING_MASTER_WORKFLOWS=5
RUNNING_MASTER_WORKFLOWS=$(curl "$REPO_API/actions/workflows/$WORKFLOW_ID/runs?branch=master&status=in_progress" --header "Authorization: Bearer $GITHUB_TOKEN" | jq -r ".total_count")
if [ "$RUNNING_MASTER_WORKFLOWS" -gt "$MAX_RUNNING_MASTER_WORKFLOWS" ]; then
  echo "More than $MAX_RUNNING_MASTER_WORKFLOWS integration tests workflows running on master."
  echo "Skipping launching workflows."
  exit 0
fi

CONNECTORS=$(./gradlew integrationTest --dry-run | grep 'integrationTest SKIPPED' | cut -d: -f 4 | sort | uniq)
echo "$CONNECTORS" | while read -r connector; do
  echo "Issuing request for connector $connector..."
  curl \
    -i \
    -X POST \
    -H "Accept: application/vnd.github.v3+json" \
    -H "Authorization: Bearer $GITHUB_TOKEN" \
    "$REPO_API/actions/workflows/$WORKFLOW_ID/dispatches" \
    -d "{\"ref\":\"master\", \"inputs\": { \"connector\": \"$connector\"} }"
done

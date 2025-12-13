#!/usr/bin/env bash

set -euo pipefail

# Creates a GitHub issue for CDK connector compatibility test failures.
# If an issue for the connector already exists, appends a new entry to the existing issue
# instead of creating a new issue.
#
# This is intended to be used by the move team since it has specific logic to how the move team manages oncall issues.
#
# Usage: tools/bin/bulk-cdk-compatibility-test/create-gh-issue.sh <connector_name> <job_url> <commit_sha>
# Example: tools/bin/bulk-cdk-compatibility-test/create-gh-issue.sh destination-dev-null www.myjoburl.com abcdef123456

# default values are specific to how the move team manages issues
# Getting these ids is not straightforward:
# - project number: from the project URL `https://github.com/orgs/airbytehq/projects/98`
# - status field id and oncall option id: using `gh project field-list 98 --owner airbytehq --format json` to explore the project fields and options
ISSUES_REPOSITORY="${ISSUES_REPOSITORY:-airbytehq/airbyte-internal-issues}"
PROJECT_NUMBER="${PROJECT_NUMBER:-98}"
STATUS_FIELD_ID="${STATUS_FIELD_ID:-PVTSSF_lADOA4_XW84Am4WkzgetXZM}"
ONCALL_OPTION_ID="${ONCALL_OPTION_ID:-3ecf8bb4}"

connector_name=$1
job_url=$2
commit_sha=$3

title="[CDK Connector Compatibility Test] Failures for $connector_name"

existing_issue_number=$(gh issue list --state open --search "$title in:title" -R $ISSUES_REPOSITORY --json number --jq '.[0].number')

# Build new entry
timestamp="$(date -u +'%Y-%m-%d %H:%M:%SZ')"
entry=$'#### ❌ '"$timestamp"$'\n'"Run: $job_url"$'\n'"Commit: ${commit_sha}"

if [ -n "${existing_issue_number:-}" ]; then
  # add new entry to existing issue
  existing_issue_body="$(gh issue view "$existing_issue_number" -R "$ISSUES_REPOSITORY" --json body --jq .body)"
  updated_issue_body="$existing_issue_body"$'\n'"${entry}"
  gh issue edit "$existing_issue_number" -R "$ISSUES_REPOSITORY" -b "$updated_issue_body"
  echo "Updated issue #${existing_issue_number} with new failure entry."
else
  # create new issue
  INITIAL_BODY=$'# Test failure history\n\n'"${entry}"
  issue_url=$(gh issue create -t "$title" -b "$INITIAL_BODY" -R $ISSUES_REPOSITORY)
  echo "Created issue ${issue_url}."
  item_id=$(gh project item-add $PROJECT_NUMBER --owner "airbytehq" --url "$issue_url" --format json --jq '.id')
  project_id=$(gh project view $PROJECT_NUMBER --owner "airbytehq" --format json --jq '.id')
  gh project item-edit \
    --id $item_id \
    --project-id $project_id \
    --field-id $STATUS_FIELD_ID \
    --single-select-option-id "$ONCALL_OPTION_ID"
  echo "Created new issue for $connector_name."
fi

#!/usr/bin/env bash

set -euo pipefail

# Builds the Slack `chat.postMessage` payload summarizing a run of the
# "Auto Upgrade CDK for Certified Connectors" workflow.
#
# Each matrix job writes a `<connector>.json` result file into the results dir:
#   {"connector": "...", "status": "upgraded|up-to-date|failed",
#    "old_cdk_version": "...", "new_cdk_version": "...",
#    "connector_version": "...", "pr_url": "..."}
# Connectors in the connector list without a result file are reported as failed.
#
# Usage:
#   build-slack-summary.sh <results_dir> <connectors_json> <slack_channel> <output_file>
#
# Expects GITHUB_REPOSITORY, GITHUB_RUN_ID and GITHUB_SERVER_URL to be set (they are, in Actions).

results_dir=$1
connectors_json=$2
slack_channel=$3
output_file=$4

run_url="${GITHUB_SERVER_URL}/${GITHUB_REPOSITORY}/actions/runs/${GITHUB_RUN_ID}"

# Merge the result files, filling in "failed" for any connector that never reported.
results=$(
  jq --null-input --compact-output \
    --argjson connectors "$connectors_json" \
    --slurpfile reported <(cat "$results_dir"/*.json 2>/dev/null || true) '
    ($reported | map({key: .connector, value: .}) | from_entries) as $by_name
    | $connectors
    | map($by_name[.] // {connector: ., status: "failed"})
  '
)

total=$(jq 'length' <<< "$results")
upgraded=$(jq --compact-output 'map(select(.status == "upgraded"))' <<< "$results")
up_to_date=$(jq --compact-output 'map(select(.status == "up-to-date"))' <<< "$results")
failed=$(jq --compact-output 'map(select(.status == "failed"))' <<< "$results")
n_upgraded=$(jq 'length' <<< "$upgraded")
n_up_to_date=$(jq 'length' <<< "$up_to_date")
n_failed=$(jq 'length' <<< "$failed")

if [[ "$total" -eq 0 ]]; then
  status_emoji=":x:"
  status_text="no connectors were processed (did the connector list step fail?)"
elif [[ "$n_failed" -gt 0 ]]; then
  status_emoji=":warning:"
  status_text="${n_failed} of ${total} connectors failed"
elif [[ "$n_upgraded" -gt 0 ]]; then
  status_emoji=":white_check_mark:"
  status_text="${n_upgraded} PR(s) opened, no failures"
else
  status_emoji=":white_check_mark:"
  status_text="all ${total} connectors already up to date"
fi

upgraded_lines=$(jq --raw-output '
  map("• <\(.pr_url)|\(.connector)> `\(.connector_version)` — CDK `\(.old_cdk_version)` → `\(.new_cdk_version)`")
  | join("\n")' <<< "$upgraded")
up_to_date_lines=$(jq --raw-output 'map("`\(.connector)`") | join(", ")' <<< "$up_to_date")
failed_lines=$(jq --raw-output --arg run_url "$run_url" '
  map("• `\(.connector)` — <\($run_url)|see job logs>" + (if (.pr_url // "") != "" then " · <\(.pr_url)|draft PR>" else "" end)) | join("\n")' <<< "$failed")

jq --null-input \
  --arg channel "$slack_channel" \
  --arg repo "$GITHUB_REPOSITORY" \
  --arg run_url "$run_url" \
  --arg run_id "$GITHUB_RUN_ID" \
  --arg status_emoji "$status_emoji" \
  --arg status_text "$status_text" \
  --arg n_upgraded "$n_upgraded" \
  --arg n_up_to_date "$n_up_to_date" \
  --arg n_failed "$n_failed" \
  --arg upgraded_lines "$upgraded_lines" \
  --arg up_to_date_lines "$up_to_date_lines" \
  --arg failed_lines "$failed_lines" '
  def section($text): {type: "section", text: {type: "mrkdwn", text: $text}};
  {
    channel: $channel,
    text: "Bulk CDK auto-upgrade (\($repo)): \($status_text)",
    blocks: (
      [
        {type: "header", text: {type: "plain_text", text: ":arrows_counterclockwise: Bulk CDK auto-upgrade", emoji: true}},
        section("\($status_emoji) *\($status_text)*  ·  `\($repo)`  ·  <\($run_url)|workflow run #\($run_id)>")
      ]
      + (if $n_upgraded != "0" then [section("*:rocket: Upgraded — PRs opened (\($n_upgraded))*\n\($upgraded_lines)")] else [] end)
      + (if $n_failed != "0" then [section("*:x: Failed (\($n_failed))*\n\($failed_lines)")] else [] end)
      + (if $n_up_to_date != "0" then [section("*:ok_hand: Already on latest CDK (\($n_up_to_date))*\n\($up_to_date_lines)")] else [] end)
    )
  }' > "$output_file"

echo "Slack payload written to $output_file"
cat "$output_file"

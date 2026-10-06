#!/usr/bin/env bash
# Classifies a PR or issue as a playbook-eval artifact created by the
# airbytehq/ai-skills eval harness (evals/framework/scenario.py).
#
# Inputs (env, all optional):
#   BASE_REF  PR base branch. `eval-base/*` is the only signal on PRs opened
#             by an eval's own Devin session (their head is `devin/...`).
#   HEAD_REF  PR head branch. Harness-created PRs use `eval/<suite>/run-...`.
#   TITLE     Harness PRs and issues are prefixed `[EVAL - DO NOT MERGE]`.
#   LABELS    Comma-separated label names. Harness applies `eval-test` after
#             creating the PR, so it can be missing on `opened` events.
#
# Prints the matching reason, or nothing if it is not an eval artifact.
set -euo pipefail

if [[ "${BASE_REF:-}" == eval-base/* ]]; then
  echo "base ${BASE_REF}"
elif [[ "${HEAD_REF:-}" == eval/* ]]; then
  echo "head ${HEAD_REF}"
elif [[ "${TITLE:-}" == "[EVAL - DO NOT MERGE]"* ]]; then
  echo "title [EVAL - DO NOT MERGE]"
elif [[ ",${LABELS:-}," == *",eval-test,"* ]]; then
  echo "label eval-test"
fi

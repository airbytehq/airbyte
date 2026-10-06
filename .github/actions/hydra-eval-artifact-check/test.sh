#!/usr/bin/env bash
# Offline test for is-eval-artifact.sh. Run: .github/actions/hydra-eval-artifact-check/test.sh
set -euo pipefail

SCRIPT="$(dirname "$0")/is-eval-artifact.sh"
failures=0

# expect <expected reason or ""> <base> <head> <title> <labels>
expect() {
  local got
  got=$(BASE_REF="$2" HEAD_REF="$3" TITLE="$4" LABELS="$5" "$SCRIPT")
  if [[ "$got" == "$1" ]]; then
    echo "ok   ${1:-<not eval>}"
  else
    echo "FAIL base='$2' head='$3' title='$4' labels='$5': expected '${1}', got '${got}'"
    failures=$((failures + 1))
  fi
}

# Eval artifacts
expect "base eval-base/prove-fix/run-1700000000-abcd1234" \
  "eval-base/prove-fix/run-1700000000-abcd1234" "devin/1700000000-fix-faker" "fix(source-faker): handle nulls" "hyd-fix"
expect "head eval/prove-fix/run-1700000000-abcd1234" \
  "master" "eval/prove-fix/run-1700000000-abcd1234" "[EVAL - DO NOT MERGE] fix" ""
expect "head eval/ai-review/run-1" "master" "eval/ai-review/run-1" "anything" ""
expect "title [EVAL - DO NOT MERGE]" "" "" "[EVAL - DO NOT MERGE] Sync fails on null cursor" ""
expect "label eval-test" "master" "feature" "normal title" "hyd-fix,eval-test"
expect "label eval-test" "" "" "" "eval-test"

# Not eval artifacts
expect "" "master" "devin/1700000000-fix-faker" "fix(source-faker): handle nulls" "hyd-fix,hyd-chain"
expect "" "master" "evaluation-tweaks" "feat: eval-base docs" "eval-testing"
expect "" "master" "fix/eval/thing" "Fix [EVAL - DO NOT MERGE] mention mid-title" "not-eval-test"
expect "" "eval-base" "pedro/x" "chore" ""
expect "" "" "" "" ""

if (( failures > 0 )); then
  echo "$failures case(s) failed"
  exit 1
fi
echo "all cases passed"

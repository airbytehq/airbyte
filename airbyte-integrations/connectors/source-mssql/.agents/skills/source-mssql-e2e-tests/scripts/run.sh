#!/usr/bin/env bash
# One-shot entrypoint for the source-mssql e2e harness.
#
# Runs the same sweep the ops repo's `connector-regression-test.yml`
# workflow runs — SPEC → CHECK → DISCOVER → configured catalog derived
# from the discover output → READ — around a local SQL Server backend
# that this script owns: start it, apply the SQL fixtures, render the
# config, run every command against that one backend, tear it down.
#
# The step order, the per-command artifact layout, the per-command
# timeouts, the "keep going and report every command" behaviour, and the
# final status that separates an infrastructure failure from a failed
# test verdict all mirror that workflow deliberately, so that CI can call
# this script instead of re-inlining the sequence in YAML and there is
# only ever one ordering to maintain.
#
# Usage:
#   run.sh [--command=all] [--fixture=PATH]… [--test-version=dev]
#          [--control-version=TAG] [--skip-read] [--step-name=NAME]
#          [--state=PATH] [--mutate=PATH]… [--replay]
#          [--catalog=PATH] [--sync-mode=full_refresh|incremental]
#          [--cursor-field=NAME] [--streams=a,b] [--config-template=PATH]
#          [--build] [--keep-backend] [-- extra airbyte-ops args…]
#
#   --command   all (default) runs the sweep; a single command
#               (spec|check|discover|read) runs just that one.
#   --skip-read runs spec/check/discover only, like the workflow's
#               skip_read_action input.
#   --state passes a saved state file to the read as --state-path.
#   --mutate runs a SQL fixture via apply-sql.sh, or an executable,
#              between replay reads. Repeat for multiple mutations.
#   --replay runs a second read after the first read passes, replaying
#             the first read's extracted state after the mutations.
#
# Passing --control-version switches airbyte-ops into comparison mode, so
# every command in the sweep emits the target-vs-control diff that Path B
# of the prove_fix playbook reports as evidence. Comparison assumes both
# images observe identical backend state; a full-refresh sweep is
# read-only, but any CDC run has to recreate the backend and the capture
# instance between the two, or the diff is meaningless while still
# looking clean.
#
# Artifacts, mirroring the workflow's /tmp/regression_test_artifacts:
#   $REPRO_OUT/<step-name>/{spec,check,discover,read}/  per-command output
#   $REPRO_OUT/<step-name>/config.json                  rendered config
#   $REPRO_OUT/<step-name>/configured_catalog.json      derived catalog
#
# Exit code: 0 when every executed command passed. 1 on a failed verdict
# or an infrastructure failure (the summary says which). A single-command
# run instead exits with the connector's own exit code, so a repro can
# still assert on it.
#
# Env: REPRO_OUT, BACKEND_NAME, BACKEND_SA_PASSWORD, BACKEND_PORT,
#      AIRBYTE_OPS, TIMEOUT_MINUTES_{SPEC,CHECK,DISCOVER,READ}
#      (see SKILL.md)
set -euo pipefail

SKILL_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SCRIPTS="$SKILL_DIR/scripts"
CONNECTOR="source-mssql"
REPRO_OUT="${REPRO_OUT:-/tmp/$CONNECTOR-repro}"
export REPRO_OUT

COMMAND="all"
FIXTURES=()
TEST_VERSION="dev"
CONTROL_VERSION_ARG=""
SKIP_READ=false
STATE_PATH=""
MUTATIONS=()
REPLAY=false
STEP_NAME=""
CATALOG=""
SYNC_MODE="full_refresh"
CURSOR_FIELD=""
STREAMS=""
CONFIG_TEMPLATE="$SKILL_DIR/fixtures/configs/base.template.json"
BUILD=false
KEEP_BACKEND=false
EXTRA_ARGS=()

# Same budgets as the workflow's per-step timeout-minutes.
declare -A TIMEOUT_MINUTES=(
  [spec]="${TIMEOUT_MINUTES_SPEC:-30}"
  [check]="${TIMEOUT_MINUTES_CHECK:-30}"
  [discover]="${TIMEOUT_MINUTES_DISCOVER:-60}"
  [read]="${TIMEOUT_MINUTES_READ:-180}"
)

while [[ $# -gt 0 ]]; do
  case "$1" in
    --command=*)         COMMAND="${1#*=}" ;;
    --fixture=*)         FIXTURES+=("${1#*=}") ;;
    --test-version=*)    TEST_VERSION="${1#*=}" ;;
    --control-version=*) CONTROL_VERSION_ARG="${1#*=}" ;;
    --skip-read)         SKIP_READ=true ;;
    --state=*)           STATE_PATH="${1#*=}" ;;
    --mutate=*)          MUTATIONS+=("${1#*=}") ;;
    --replay)            REPLAY=true ;;
    --step-name=*)       STEP_NAME="${1#*=}" ;;
    --catalog=*)         CATALOG="${1#*=}" ;;
    --sync-mode=*)       SYNC_MODE="${1#*=}" ;;
    --cursor-field=*)    CURSOR_FIELD="${1#*=}" ;;
    --streams=*)         STREAMS="${1#*=}" ;;
    --config-template=*) CONFIG_TEMPLATE="${1#*=}" ;;
    --build)             BUILD=true ;;
    --keep-backend)      KEEP_BACKEND=true ;;
    --)                  shift; EXTRA_ARGS=("$@"); break ;;
    -h|--help)           sed -n '2,50p' "${BASH_SOURCE[0]}"; exit 0 ;;
    *) echo "[run] unknown argument: $1" >&2; exit 2 ;;
  esac
  shift
done

COMMANDS=()
case "$COMMAND" in
  all)                      COMMANDS=(spec check discover read) ;;
  spec|check|discover|read) COMMANDS=("$COMMAND") ;;
  *) echo "[run] --command must be all|spec|check|discover|read (got '$COMMAND')" >&2; exit 2 ;;
esac
if [[ "$REPLAY" == true && -n "$CONTROL_VERSION_ARG" ]]; then
  echo "[run] --replay cannot be combined with --control-version: comparison runs control and target in one airbyte-ops invocation, so the backend/capture state cannot be reset between replay reads." >&2
  exit 2
fi
if [[ "$REPLAY" != true && ${#MUTATIONS[@]} -gt 0 ]]; then
  echo "[run] --mutate requires --replay: mutations are only applied between replay reads." >&2
  exit 2
fi
if [[ "$SKIP_READ" == true ]]; then
  REQUESTED=()
  for cmd in "${COMMANDS[@]}"; do
    [[ "$cmd" == read ]] || REQUESTED+=("$cmd")
  done
  COMMANDS=(${REQUESTED[@]+"${REQUESTED[@]}"})
  if [[ ${#COMMANDS[@]} -eq 0 ]]; then
    echo "[run] --skip-read left nothing to run" >&2
    exit 2
  fi
fi
SINGLE_COMMAND=false
[[ ${#COMMANDS[@]} -eq 1 ]] && SINGLE_COMMAND=true

if [[ ${#FIXTURES[@]} -eq 0 ]]; then
  FIXTURES=("$SKILL_DIR/fixtures/sql/00-init-base.sql")
fi
if [[ -z "$STEP_NAME" ]]; then
  STEP_NAME="${COMMAND/all/sweep}-$TEST_VERSION${CONTROL_VERSION_ARG:+-vs-$CONTROL_VERSION_ARG}"
fi

# The harness pulls published control tags itself but cannot build :dev.
if [[ "$TEST_VERSION" == "dev" ]] && { [[ "$BUILD" == true ]] \
  || ! docker image inspect "airbyte/$CONNECTOR:dev" >/dev/null 2>&1; }; then
  REPO_ROOT="$(git -C "$SKILL_DIR" rev-parse --show-toplevel)"
  echo "[run] building airbyte/$CONNECTOR:dev from the current checkout" >&2
  "$REPO_ROOT/gradlew" ":airbyte-integrations:connectors:$CONNECTOR:airbyteDocker" \
    --configure-on-demand
fi

# shellcheck disable=SC2329
cleanup() {
  if [[ "$KEEP_BACKEND" == true ]]; then
    echo "[run] --keep-backend: leaving the backend up; stop it with scripts/stop-backend.sh" >&2
  else
    "$SCRIPTS/stop-backend.sh" || true
  fi
}
trap cleanup EXIT

# The workflow's checkout + dependency install has no analogue here; its
# equivalent for a database source is standing up the upstream itself.
"$SCRIPTS/start-backend.sh"
for fixture in "${FIXTURES[@]}"; do
  "$SCRIPTS/apply-sql.sh" "$fixture"
done

# "Setup paths and args": everything derived once, upfront.
ARTIFACTS_DIR="$REPRO_OUT/$STEP_NAME"
CONFIGURED_CATALOG_PATH="$ARTIFACTS_DIR/configured_catalog.json"
WORKING_CONFIG="$ARTIFACTS_DIR/config.json"
rm -rf "$ARTIFACTS_DIR"
mkdir -p "$ARTIFACTS_DIR"
"$SCRIPTS/render-config.sh" "$CONFIG_TEMPLATE" "$WORKING_CONFIG"

declare -A STATUS=() RC=() NOTE=()
EXECUTED_STEPS=()

run_step() {
  local cmd="$1"
  local step_name="$2"
  shift 2
  local out_dir="$ARTIFACTS_DIR/$step_name"
  local mins="${TIMEOUT_MINUTES[$cmd]}"
  local -a limit=()
  command -v timeout >/dev/null 2>&1 && limit=(timeout "${mins}m")

  echo "[run] $step_name ($cmd)" >&2
  set +e
  REPRO_OUT="$ARTIFACTS_DIR" CONTROL_VERSION="$CONTROL_VERSION_ARG" \
    ${limit[@]+"${limit[@]}"} "$SCRIPTS/run-protocol-cmd.sh" "$cmd" "$step_name" \
    "$TEST_VERSION" "$@" ${EXTRA_ARGS[@]+"${EXTRA_ARGS[@]}"}
  local rc=$?
  set -e

  RC["$step_name"]="$rc"
  EXECUTED_STEPS+=("$step_name")
  # A missing report means the run never got far enough to produce a
  # verdict, which is the local equivalent of the workflow's
  # internal_failure: an infrastructure problem, not a test result.
  if (( rc == 124 )); then
    STATUS["$step_name"]=internal
    NOTE["$step_name"]="timed out after ${mins}m"
  elif [[ ! -f "$out_dir/report.md" ]]; then
    STATUS["$step_name"]=internal
    NOTE["$step_name"]="no report.md — the run produced no verdict"
  elif (( rc == 0 )); then
    STATUS["$step_name"]=pass
  else
    STATUS["$step_name"]=fail
    if grep -qE '^\*\*Result:\*\*.*Both versions failed' "$out_dir/report.md" 2>/dev/null; then
      NOTE["$step_name"]="both versions failed — inconclusive"
    fi
  fi
}

record_internal_step() {
  local step_name="$1"
  local rc="$2"
  local note="$3"
  RC["$step_name"]="$rc"
  STATUS["$step_name"]=internal
  NOTE["$step_name"]="$note"
  EXECUTED_STEPS+=("$step_name")
}

run_mutations() {
  local mutation
  for mutation in "${MUTATIONS[@]}"; do
    echo "[run] mutate $mutation" >&2
    if [[ "$mutation" == *.sql ]]; then
      "$SCRIPTS/apply-sql.sh" "$mutation"
    elif [[ -x "$mutation" ]]; then
      "$mutation"
    else
      echo "[run] mutation is neither a .sql file nor executable: $mutation" >&2
      return 2
    fi
  done
}

replay_reads() {
  local first_step="$1"
  local first_out="$ARTIFACTS_DIR/$first_step/stdout.txt"
  local state_1="$ARTIFACTS_DIR/state-1.json"
  local state_2="$ARTIFACTS_DIR/state-2.json"
  local mutation_rc

  if [[ "${STATUS[$first_step]:-}" != pass ]]; then
    record_internal_step read-2 1 "replay skipped because $first_step did not pass"
    return
  fi

  set +e
  "$SCRIPTS/extract-state.py" "$first_out" > "$state_1"
  local extract_rc=$?
  set -e
  if (( extract_rc != 0 )); then
    record_internal_step read-2 "$extract_rc" "replay skipped because $first_step emitted no STATE"
    return
  fi

  set +e
  run_mutations
  mutation_rc=$?
  set -e
  if (( mutation_rc != 0 )); then
    record_internal_step read-2 "$mutation_rc" "replay skipped because a mutation failed"
    return
  fi

  run_step read read-2 "--config-path=$WORKING_CONFIG" "--catalog-path=$CATALOG" \
    "--state-path=$state_1"

  if [[ "${STATUS[read-2]:-}" == pass ]]; then
    set +e
    "$SCRIPTS/extract-state.py" "$ARTIFACTS_DIR/read-2/stdout.txt" > "$state_2"
    extract_rc=$?
    set -e
    if (( extract_rc != 0 )); then
      STATUS[read-2]=internal
      RC[read-2]="$extract_rc"
      NOTE[read-2]="read passed but emitted no STATE"
    fi
  fi
}

for cmd in "${COMMANDS[@]}"; do
  case "$cmd" in
    spec)
      run_step spec spec
      ;;
    check|discover)
      run_step "$cmd" "$cmd" "--config-path=$WORKING_CONFIG"
      ;;
    read)
      # The workflow generates the configured catalog from the discover
      # step's own output rather than running a second discover, and
      # prefers the target's messages. Derive it mechanically for the
      # same reason it does: a hand-written catalog drifts from the
      # fixture, and bulk-CDK then rejects the read as bad config.
      if [[ -z "$CATALOG" ]]; then
        DISCOVER_DIR="$ARTIFACTS_DIR/discover"
        [[ -d "$DISCOVER_DIR/target" ]] && DISCOVER_DIR="$DISCOVER_DIR/target"
        if [[ ! -d "$DISCOVER_DIR" ]]; then
          # No discover in this invocation (a bare --command=read), so
          # run one just for the catalog.
          DISCOVER_DIR="$ARTIFACTS_DIR/catalog-discover"
          run_step discover catalog-discover "--config-path=$WORKING_CONFIG"
          if [[ "${STATUS[catalog-discover]:-}" != pass ]]; then
            continue
          fi
        fi
        set +e
        STREAMS="$STREAMS" SYNC_MODE="$SYNC_MODE" CURSOR_FIELD="$CURSOR_FIELD" \
          "$SCRIPTS/make-catalog.sh" "$DISCOVER_DIR" "$CONFIGURED_CATALOG_PATH"
        CATALOG_RC=$?
        set -e
        if (( CATALOG_RC != 0 )); then
          record_internal_step read "$CATALOG_RC" \
            "could not derive a configured catalog from $DISCOVER_DIR"
          continue
        fi
        CATALOG="$CONFIGURED_CATALOG_PATH"
      fi
      READ_STEP="read"
      READ_ARGS=("--config-path=$WORKING_CONFIG" "--catalog-path=$CATALOG")
      [[ -n "$STATE_PATH" ]] && READ_ARGS+=("--state-path=$STATE_PATH")
      if [[ "$REPLAY" == true ]]; then
        READ_STEP="read-1"
      fi
      run_step read "$READ_STEP" "${READ_ARGS[@]}"
      if [[ "$REPLAY" == true ]]; then
        replay_reads "$READ_STEP"
      fi
      ;;
  esac
done

# "Determine Final Status" plus "Write Summary Table": one line per
# command, every non-pass rendered as a failure, and the infrastructure
# failures called out separately so a broken run is never read as a
# regression.
INTERNAL_FAILURE=false
ALL_PASSED=true
SUMMARY="| Command | Result |
|---------|--------|"
for step_name in "${EXECUTED_STEPS[@]}"; do
  cell=""
  case "${STATUS[$step_name]:-}" in
    pass)     cell="PASS" ;;
    fail)     cell="FAIL"; ALL_PASSED=false ;;
    internal) cell="ERROR"; ALL_PASSED=false; INTERNAL_FAILURE=true ;;
  esac
  [[ -z "$cell" ]] && continue
  [[ -n "${NOTE[$step_name]:-}" ]] && cell="$cell (${NOTE[$step_name]})"
  SUMMARY+="
| \`${step_name^^}\` | $cell |"
done
if [[ "$COMMAND" == all && "$SKIP_READ" == true ]]; then
  SUMMARY+="
| \`READ\` | _(skipped)_ |"
fi
SUMMARY+="

Artifacts: \`$ARTIFACTS_DIR/<step>/\` (\`report.md\`, \`stdout.txt\`, \`stderr.txt\`)."

echo "$SUMMARY" >&2
# CI gets the same table in the run summary without the workflow having
# to reconstruct it from parsed output.
if [[ -n "${GITHUB_STEP_SUMMARY:-}" ]]; then
  printf "## \`%s\` regression sweep\n\n%s\n" "$CONNECTOR" "$SUMMARY" \
    >> "$GITHUB_STEP_SUMMARY"
fi

if [[ "$INTERNAL_FAILURE" == true ]]; then
  echo "[run] infrastructure failure — the verdict above is not a test result" >&2
fi

# A single-command run keeps returning the connector's own exit code, so
# repro scripts can assert on it; a sweep has more than one, so it
# reports pass/fail like the workflow's job status.
if [[ "$SINGLE_COMMAND" == true ]]; then
  LAST_STEP="${EXECUTED_STEPS[${#EXECUTED_STEPS[@]}-1]:-}"
  exit "${RC[$LAST_STEP]:-1}"
fi
[[ "$ALL_PASSED" == true ]] || exit 1
exit 0

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
#          [--control-version=TAG] [--reset=none|fixture|backend]
#          [--skip-read] [--step-name=NAME] [--catalog=PATH]
#          [--state=PATH] [--sync-mode=full_refresh|incremental]
#          [--cursor-field=NAME] [--streams=a,b] [--config-template=PATH]
#          [--build] [--keep-backend] [-- extra airbyte-ops args…]
#
#   --state passes a saved state file to the read step as
#           `--state-path`. Meant for multi-phase drivers: a first
#           `run.sh` writes the read's stdout, the driver extracts a
#           STATE file with `extract-state.py`, and a second `run.sh`
#           passes that state back via `--state=…`.
#
#   --command   all (default) runs the sweep; a single command
#               (spec|check|discover|read) runs just that one.
#   --skip-read runs spec/check/discover only, like the workflow's
#               skip_read_action input.
#
# Comparison modes (with --control-version):
#
#   --reset=none (default): one airbyte-ops call per command with both
#     --test-image and --control-image. airbyte-ops runs the two images
#     sequentially against one backend and emits a target-vs-control
#     diff via its built-in comparators. This is the right default for
#     non-CDC full-refresh work, where the diff is meaningful and cheap.
#
#   --reset=fixture: run the whole sweep against the control image
#     first, drop every non-system database, re-apply the fixtures, then
#     run the sweep against the target image. Two single-version runs,
#     no airbyte-ops comparator. Faster than --reset=backend but the
#     SQL Server log-LSN clock keeps ticking, so per-record LSN columns
#     and STATE offsets differ between the two runs. Right for CDC
#     comparisons where a shared capture instance would poison the diff.
#
#   --reset=backend: same as --reset=fixture but also recreates the
#     backend container between the two runs, resetting the LSN clock at
#     ~15s of extra startup cost. Use when the reproduction depends on
#     matching LSN sequences across runs.
#
# Artifacts, mirroring the workflow's /tmp/regression_test_artifacts:
#   $REPRO_OUT/<step-name>/{spec,check,discover,read}/  per-command output
#   $REPRO_OUT/<step-name>/config.json                  rendered config
#   $REPRO_OUT/<step-name>/configured_catalog.json      derived catalog
#
#   Under --reset=fixture|backend the per-command dirs are further nested
#   under control/ and target/ so both sides' artifacts survive.
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
RESET="none"
SKIP_READ=false
STEP_NAME=""
CATALOG=""
STATE_PATH=""
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
    --reset=*)           RESET="${1#*=}" ;;
    --skip-read)         SKIP_READ=true ;;
    --step-name=*)       STEP_NAME="${1#*=}" ;;
    --catalog=*)         CATALOG="${1#*=}" ;;
    --state=*)           STATE_PATH="${1#*=}" ;;
    --sync-mode=*)       SYNC_MODE="${1#*=}" ;;
    --cursor-field=*)    CURSOR_FIELD="${1#*=}" ;;
    --streams=*)         STREAMS="${1#*=}" ;;
    --config-template=*) CONFIG_TEMPLATE="${1#*=}" ;;
    --build)             BUILD=true ;;
    --keep-backend)      KEEP_BACKEND=true ;;
    --)                  shift; EXTRA_ARGS=("$@"); break ;;
    -h|--help)           sed -n '2,72p' "${BASH_SOURCE[0]}"; exit 0 ;;
    *) echo "[run] unknown argument: $1" >&2; exit 2 ;;
  esac
  shift
done

case "$RESET" in
  none|fixture|backend) ;;
  *) echo "[run] --reset must be none|fixture|backend (got '$RESET')" >&2; exit 2 ;;
esac

COMMANDS=()
case "$COMMAND" in
  all)                      COMMANDS=(spec check discover read) ;;
  spec|check|discover|read) COMMANDS=("$COMMAND") ;;
  *) echo "[run] --command must be all|spec|check|discover|read (got '$COMMAND')" >&2; exit 2 ;;
esac
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

# --reset only has anything to reset between when there are two image
# runs. Fall back to none in single-version mode and warn — silently
# ignoring the flag would hide a misconfigured caller.
if [[ "$RESET" != none && -z "$CONTROL_VERSION_ARG" ]]; then
  echo "[run] --reset=$RESET has no effect without --control-version; treating as --reset=none" >&2
  RESET=none
fi
PER_IMAGE_SWEEPS=false
[[ -n "$CONTROL_VERSION_ARG" && "$RESET" != none ]] && PER_IMAGE_SWEEPS=true

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
  "$REPO_ROOT/gradlew" ":airbyte-integrations:connectors:$CONNECTOR:dockerBuildx" \
    --configure-on-demand
fi

cleanup() {
  if [[ "$KEEP_BACKEND" == true ]]; then
    echo "[run] --keep-backend: leaving the backend up; stop it with scripts/stop-backend.sh" >&2
  else
    "$SCRIPTS/stop-backend.sh" || true
  fi
}
trap cleanup EXIT

apply_fixtures() {
  for fixture in "${FIXTURES[@]}"; do
    "$SCRIPTS/apply-sql.sh" "$fixture"
  done
}

# The workflow's checkout + dependency install has no analogue here; its
# equivalent for a database source is standing up the upstream itself.
"$SCRIPTS/start-backend.sh"
apply_fixtures

ARTIFACTS_DIR="$REPRO_OUT/$STEP_NAME"
CONFIGURED_CATALOG_PATH="$ARTIFACTS_DIR/configured_catalog.json"
WORKING_CONFIG="$ARTIFACTS_DIR/config.json"
rm -rf "$ARTIFACTS_DIR"
mkdir -p "$ARTIFACTS_DIR"
"$SCRIPTS/render-config.sh" "$CONFIG_TEMPLATE" "$WORKING_CONFIG"

# Under --reset=fixture|backend we run two full single-version sweeps
# with a reset between them. Every STATUS/RC/NOTE entry is prefixed by
# the side (control/target); on the shared path the prefix is empty so
# the summary code below reads a single set of entries.
declare -A STATUS=() RC=() NOTE=()
SIDE=""

run_step() {
  local cmd="$1"; shift
  local key="${SIDE:+${SIDE}.}${cmd}"
  local out_dir="$ARTIFACTS_DIR${SIDE:+/$SIDE}/$cmd"
  local run_version="${STEP_VERSION:-$TEST_VERSION}"
  # When we're driving each image with its own single-version call,
  # unset CONTROL_VERSION so run-protocol-cmd.sh takes the single-version
  # branch even though the outer script has one. Otherwise leave it as
  # today so the built-in comparator runs.
  local run_control="$CONTROL_VERSION_ARG"
  [[ "$PER_IMAGE_SWEEPS" == true ]] && run_control=""
  local mins="${TIMEOUT_MINUTES[$cmd]}"
  local -a limit=()
  command -v timeout >/dev/null 2>&1 && limit=(timeout "${mins}m")

  echo "[run] ${SIDE:+$SIDE }$cmd" >&2
  set +e
  REPRO_OUT="$ARTIFACTS_DIR${SIDE:+/$SIDE}" CONTROL_VERSION="$run_control" \
    ${limit[@]+"${limit[@]}"} "$SCRIPTS/run-protocol-cmd.sh" "$cmd" "$cmd" \
    "$run_version" "$@" ${EXTRA_ARGS[@]+"${EXTRA_ARGS[@]}"}
  local rc=$?
  set -e

  RC["$key"]="$rc"
  # A missing report means the run never got far enough to produce a
  # verdict, which is the local equivalent of the workflow's
  # internal_failure: an infrastructure problem, not a test result.
  if (( rc == 124 )); then
    STATUS["$key"]=internal
    NOTE["$key"]="timed out after ${mins}m"
  elif [[ ! -f "$out_dir/report.md" ]]; then
    STATUS["$key"]=internal
    NOTE["$key"]="no report.md — the run produced no verdict"
  elif (( rc == 0 )); then
    STATUS["$key"]=pass
  else
    STATUS["$key"]=fail
    if grep -qE '^\*\*Result:\*\*.*Both versions failed' "$out_dir/report.md" 2>/dev/null; then
      NOTE["$key"]="both versions failed — inconclusive"
    fi
  fi
}

sweep() {
  # Run the requested COMMANDS list under the current SIDE and
  # STEP_VERSION, deriving the read catalog from this side's own
  # discover output when the caller did not pass an explicit one.
  local side_catalog="$CATALOG"
  local side_artifacts="$ARTIFACTS_DIR${SIDE:+/$SIDE}"
  mkdir -p "$side_artifacts"

  for cmd in "${COMMANDS[@]}"; do
    case "$cmd" in
      spec)
        run_step spec
        ;;
      check|discover)
        run_step "$cmd" "--config-path=$WORKING_CONFIG"
        ;;
      read)
        # A derived catalog needs a discover that produced one. When
        # discover already failed on this side — the correct outcome for
        # an invalid config — read did not run, so it is neither a
        # verdict nor an infrastructure failure. An explicit --catalog
        # bypasses discover so that case still runs.
        local disc_key="${SIDE:+${SIDE}.}discover"
        if [[ -z "$side_catalog" && -n "${STATUS[$disc_key]:-}" \
          && "${STATUS[$disc_key]}" != pass ]]; then
          STATUS["${SIDE:+${SIDE}.}read"]=skipped
          NOTE["${SIDE:+${SIDE}.}read"]="discover did not produce a catalog"
          continue
        fi
        if [[ -z "$side_catalog" ]]; then
          local disc_dir="$side_artifacts/discover"
          [[ -d "$disc_dir/target" ]] && disc_dir="$disc_dir/target"
          if [[ ! -d "$disc_dir" ]]; then
            # No discover in this invocation (a bare --command=read),
            # so run one just for the catalog.
            disc_dir="$side_artifacts/catalog-discover"
            set +e
            REPRO_OUT="$side_artifacts" "$SCRIPTS/run-protocol-cmd.sh" \
              discover catalog-discover "${STEP_VERSION:-$TEST_VERSION}" \
              "--config-path=$WORKING_CONFIG"
            local disc_rc=$?
            set -e
            if (( disc_rc != 0 )); then
              STATUS["${SIDE:+${SIDE}.}read"]=internal
              RC["${SIDE:+${SIDE}.}read"]="$disc_rc"
              NOTE["${SIDE:+${SIDE}.}read"]="catalog discover failed — see $disc_dir"
              continue
            fi
          fi
          local catalog_out="$side_artifacts/configured_catalog.json"
          set +e
          STREAMS="$STREAMS" SYNC_MODE="$SYNC_MODE" CURSOR_FIELD="$CURSOR_FIELD" \
            "$SCRIPTS/make-catalog.sh" "$disc_dir" "$catalog_out"
          local cat_rc=$?
          set -e
          if (( cat_rc != 0 )); then
            STATUS["${SIDE:+${SIDE}.}read"]=internal
            RC["${SIDE:+${SIDE}.}read"]="$cat_rc"
            NOTE["${SIDE:+${SIDE}.}read"]="could not derive a configured catalog from $disc_dir"
            continue
          fi
          side_catalog="$catalog_out"
        fi
        local -a read_args=(
          "--config-path=$WORKING_CONFIG"
          "--catalog-path=$side_catalog"
        )
        [[ -n "$STATE_PATH" ]] && read_args+=("--state-path=$STATE_PATH")
        run_step read "${read_args[@]}"
        ;;
    esac
  done
}

reset_between_images() {
  case "$RESET" in
    fixture)
      echo "[run] --reset=fixture: dropping non-system databases and re-applying fixtures" >&2
      "$SCRIPTS/reset-databases.sh"
      apply_fixtures
      "$SCRIPTS/render-config.sh" "$CONFIG_TEMPLATE" "$WORKING_CONFIG"
      ;;
    backend)
      echo "[run] --reset=backend: recreating the backend container" >&2
      "$SCRIPTS/stop-backend.sh"
      "$SCRIPTS/start-backend.sh"
      apply_fixtures
      # Backend recreation may have assigned a new bridge IP.
      "$SCRIPTS/render-config.sh" "$CONFIG_TEMPLATE" "$WORKING_CONFIG"
      ;;
  esac
}

if [[ "$PER_IMAGE_SWEEPS" == true ]]; then
  SIDE=control STEP_VERSION="$CONTROL_VERSION_ARG" sweep
  reset_between_images
  SIDE=target  STEP_VERSION="$TEST_VERSION"        sweep
else
  sweep
fi

# "Determine Final Status" plus "Write Summary Table": one line per
# command, every non-pass rendered as a failure, and the infrastructure
# failures called out separately so a broken run is never read as a
# regression.
INTERNAL_FAILURE=false
ALL_PASSED=true

# Pure: emit the table cell for one command. Called under `$(...)` so
# any variable assignment here would evaporate — see `update_flags`.
status_cell() {
  local key="$1" note_key="$2"
  case "${STATUS[$key]:-}" in
    "")       [[ "$COMMAND" == all ]] && echo "_(skipped)_" || echo "" ;;
    pass)     echo "PASS" ;;
    fail)     local out="FAIL"; [[ -n "${NOTE[$note_key]:-}" ]] && out+=" (${NOTE[$note_key]})"; echo "$out" ;;
    skipped)  local out="SKIPPED"; [[ -n "${NOTE[$note_key]:-}" ]] && out+=" (${NOTE[$note_key]})"; echo "$out" ;;
    internal) local out="ERROR"; [[ -n "${NOTE[$note_key]:-}" ]] && out+=" (${NOTE[$note_key]})"; echo "$out" ;;
  esac
}

# Side-effectful: called in the parent shell so it can mutate the
# ALL_PASSED / INTERNAL_FAILURE flags the exit path reads.
update_flags() {
  case "${STATUS[$1]:-}" in
    fail)     ALL_PASSED=false ;;
    internal) ALL_PASSED=false; INTERNAL_FAILURE=true ;;
  esac
}

if [[ "$PER_IMAGE_SWEEPS" == true ]]; then
  SUMMARY="| Command | Control (\`$CONTROL_VERSION_ARG\`) | Target (\`$TEST_VERSION\`) |
|---------|---------|---------|"
  for cmd in spec check discover read; do
    c_cell="$(status_cell "control.$cmd" "control.$cmd")"
    t_cell="$(status_cell "target.$cmd" "target.$cmd")"
    update_flags "control.$cmd"
    update_flags "target.$cmd"
    [[ -z "$c_cell" && -z "$t_cell" ]] && continue
    SUMMARY+="
| \`$(echo "$cmd" | tr '[:lower:]' '[:upper:]')\` | ${c_cell:-—} | ${t_cell:-—} |"
  done
else
  SUMMARY="| Command | Result |
|---------|--------|"
  for cmd in spec check discover read; do
    cell="$(status_cell "$cmd" "$cmd")"
    update_flags "$cmd"
    [[ -z "$cell" ]] && continue
    SUMMARY+="
| \`$(echo "$cmd" | tr '[:lower:]' '[:upper:]')\` | $cell |"
  done
fi

if [[ "$PER_IMAGE_SWEEPS" == true ]]; then
  SUMMARY+="

Artifacts: \`$ARTIFACTS_DIR/{control,target}/<command>/\` (\`report.md\`, \`stdout.txt\`, \`stderr.txt\`)."
else
  SUMMARY+="

Artifacts: \`$ARTIFACTS_DIR/<command>/\` (\`report.md\`, \`stdout.txt\`, \`stderr.txt\`)."
fi

echo "$SUMMARY" >&2
# CI gets the same table in the run summary without the workflow having
# to reconstruct it from parsed output.
if [[ -n "${GITHUB_STEP_SUMMARY:-}" ]]; then
  printf '## `%s` regression sweep\n\n%s\n' "$CONNECTOR" "$SUMMARY" \
    >> "$GITHUB_STEP_SUMMARY"
fi

if [[ "$INTERNAL_FAILURE" == true ]]; then
  echo "[run] infrastructure failure — the verdict above is not a test result" >&2
fi

# A single-command run keeps returning the connector's own exit code, so
# repro scripts can assert on it; a sweep has more than one, so it
# reports pass/fail like the workflow's job status. In per-image mode a
# single-command run is still a single logical command that was executed
# on both sides — surface the target's exit code, which is the fix under
# test.
if [[ "$SINGLE_COMMAND" == true ]]; then
  if [[ "$PER_IMAGE_SWEEPS" == true ]]; then
    exit "${RC["target.${COMMANDS[0]}"]:-1}"
  fi
  exit "${RC[${COMMANDS[0]}]:-1}"
fi
[[ "$ALL_PASSED" == true ]] || exit 1
exit 0

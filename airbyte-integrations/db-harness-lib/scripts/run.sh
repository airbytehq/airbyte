#!/usr/bin/env bash
# One-shot entrypoint for a database connector e2e harness.
#
# Runs the same sweep the ops repo's `connector-regression-test.yml`
# workflow runs — SPEC → CHECK → DISCOVER → configured catalog derived
# from the discover output → READ — around a local database backend that
# this script owns (via the engine's lifecycle scripts): start it, apply
# the SQL fixtures, render the config, run every command against that one
# backend, tear it down.
#
# The step order, the per-command artifact layout, the per-command
# timeouts, the "keep going and report every command" behaviour, and the
# final status that separates an infrastructure failure from a failed
# test verdict all mirror that workflow deliberately, so that CI can call
# this script instead of re-inlining the sequence in YAML and there is
# only ever one ordering to maintain.
#
# Usage:
#   run.sh [--command=all] [--fixture=PATH]… [--skip-fixtures]
#          [--test-version=dev] [--control-version=TAG]
#          [--reset=none|fixture|backend] [--skip-read]
#          [--step-name=NAME] [--catalog=PATH] [--state=PATH]
#          [--sync-mode=full_refresh|incremental] [--cursor-field=NAME]
#          [--streams=a,b] [--config-template=PATH]
#          [--expect-test=pass|fail] [--expect-control=pass|fail]
#          [--min-records=N] [--min-states=N]
#          [--expect-match=[<command>:]<channel>:<regex>[:N]]…
#          [--forbid-match=[<command>:]<channel>:<regex>]…
#          [--build] [--keep-backend] [-- extra airbyte-ops args…]
#
#   --skip-fixtures runs the sweep against whatever state the backend
#           already has, without applying any fixtures. Used by
#           multi-phase driver scripts on the second/later `run.sh`
#           invocation, when re-applying the initial fixture would wipe
#           the intermediate state a preceding phase established. Fails
#           if any `--fixture=` is also passed (either apply fixtures
#           or skip them — asking for both is a caller bug).
#
#   --state passes a saved state file to the read step as
#           `--state-path`. Meant for multi-phase drivers: a first
#           `run.sh` writes the read's stdout, the driver extracts a
#           STATE file with `extract-state.py`, and a second `run.sh`
#           passes that state back via `--state=…`.
#
#   --expect-*, --min-*, --expect-match, --forbid-match declaratively
#          gate the run's exit code, replacing the `grep -q '…' || exit 1`
#          boilerplate driver scripts currently hand-roll. All
#          assertions apply to target-side artifacts; --expect-control
#          gates the control sweep's overall verdict under
#          --control-version (only useful in comparison modes).
#          Match-spec grammar: [<command>:]<channel>:<regex>[:N] where
#          <command> ∈ spec|check|discover|read (defaults to read if
#          omitted) and <channel> ∈ stdout|stderr|any. `check:stderr:…`
#          reads target's check step; a bare `stderr:…` reads target's
#          read step, unchanged from prior behavior. Match-count
#          defaults to 1. --min-records / --min-states are read-step
#          only (they count RECORD / STATE envelopes, which are
#          read-specific). Any expectation failure exits non-zero
#          regardless of the command-level verdicts.
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

LIB_SCRIPTS="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ENGINE_SCRIPTS_DIR="${ENGINE_SCRIPTS_DIR:?engine shim must export ENGINE_SCRIPTS_DIR}"
STOP_BACKEND="$ENGINE_SCRIPTS_DIR/stop-backend.sh"
[[ -x "$STOP_BACKEND" ]] || STOP_BACKEND="$LIB_SCRIPTS/stop-backend.sh"
CONNECTOR="${CONNECTOR:?engine shim must export CONNECTOR}"
REPRO_OUT="${REPRO_OUT:-/tmp/$CONNECTOR-repro}"
export REPRO_OUT

COMMAND="all"
FIXTURES=()
SKIP_FIXTURES=false
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
CONFIG_TEMPLATE=""
BUILD=false
KEEP_BACKEND=false
EXTRA_ARGS=()

# Runner-enforced expectations. Empty / -1 means "no assertion." Arrays
# hold raw `<channel>:<regex>[:N]` specs, parsed lazily at check time
# so a bad regex fails there with the argument that caused it rather
# than at argparse.
EXPECT_TEST=""
EXPECT_CONTROL=""
MIN_RECORDS=-1
MIN_STATES=-1
EXPECT_MATCHES=()
FORBID_MATCHES=()
EXPECTATION_FAILURES=()

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
    --skip-fixtures)     SKIP_FIXTURES=true ;;
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
    --expect-test=*)     EXPECT_TEST="${1#*=}" ;;
    --expect-control=*)  EXPECT_CONTROL="${1#*=}" ;;
    --min-records=*)     MIN_RECORDS="${1#*=}" ;;
    --min-states=*)      MIN_STATES="${1#*=}" ;;
    --expect-match=*)    EXPECT_MATCHES+=("${1#*=}") ;;
    --forbid-match=*)    FORBID_MATCHES+=("${1#*=}") ;;
    --build)             BUILD=true ;;
    --keep-backend)      KEEP_BACKEND=true ;;
    --)                  shift; EXTRA_ARGS=("$@"); break ;;
    -h|--help)           sed -n '2,100p' "${BASH_SOURCE[0]}"; exit 0 ;;
    *) echo "[run] unknown argument: $1" >&2; exit 2 ;;
  esac
  shift
done

case "$RESET" in
  none|fixture|backend) ;;
  *) echo "[run] --reset must be none|fixture|backend (got '$RESET')" >&2; exit 2 ;;
esac

for v in "$EXPECT_TEST" "$EXPECT_CONTROL"; do
  case "$v" in
    ""|pass|fail) ;;
    *) echo "[run] --expect-test / --expect-control must be pass|fail (got '$v')" >&2; exit 2 ;;
  esac
done
if [[ -n "$EXPECT_CONTROL" && -z "$CONTROL_VERSION_ARG" ]]; then
  echo "[run] --expect-control requires --control-version" >&2
  exit 2
fi
if [[ -n "$EXPECT_CONTROL" && "$RESET" == none ]]; then
  echo "[run] --expect-control requires --reset=fixture or --reset=backend" >&2
  exit 2
fi
for n in "$MIN_RECORDS" "$MIN_STATES"; do
  [[ "$n" == -1 || "$n" =~ ^[0-9]+$ ]] || {
    echo "[run] --min-records / --min-states must be a non-negative integer (got '$n')" >&2
    exit 2
  }
done

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

if [[ "$SKIP_FIXTURES" == true && ${#FIXTURES[@]} -gt 0 ]]; then
  echo "[run] --skip-fixtures + --fixture= is inconsistent (either apply fixtures or skip them)" >&2
  exit 2
fi
if [[ "$SKIP_FIXTURES" != true && ${#FIXTURES[@]} -eq 0 ]]; then
  FIXTURES=("${DEFAULT_FIXTURE:?engine shim must export DEFAULT_FIXTURE}")
fi
if [[ -z "$STEP_NAME" ]]; then
  STEP_NAME="${COMMAND/all/sweep}-$TEST_VERSION${CONTROL_VERSION_ARG:+-vs-$CONTROL_VERSION_ARG}"
fi

# The harness pulls published control tags itself but cannot build :dev.
if [[ "$TEST_VERSION" == "dev" ]] && { [[ "$BUILD" == true ]] \
  || ! docker image inspect "airbyte/$CONNECTOR:dev" >/dev/null 2>&1; }; then
  REPO_ROOT="$(git -C "$LIB_SCRIPTS" rev-parse --show-toplevel)"
  echo "[run] building airbyte/$CONNECTOR:dev from the current checkout" >&2
  "$REPO_ROOT/gradlew" ":airbyte-integrations:connectors:$CONNECTOR:dockerBuildx" \
    --configure-on-demand
fi

# shellcheck disable=SC2329
cleanup() {
  if [[ "$KEEP_BACKEND" == true ]]; then
    echo "[run] --keep-backend: leaving the backend up; stop it with $STOP_BACKEND" >&2
  else
    "$STOP_BACKEND" || true
  fi
}
trap cleanup EXIT

apply_fixtures() {
  [[ "$SKIP_FIXTURES" == true ]] && return 0
  for fixture in "${FIXTURES[@]}"; do
    "$ENGINE_SCRIPTS_DIR/apply-sql.sh" "$fixture"
  done
}

# The workflow's checkout + dependency install has no analogue here; its
# equivalent for a database source is standing up the upstream itself.
"$ENGINE_SCRIPTS_DIR/start-backend.sh"
apply_fixtures

ARTIFACTS_DIR="$REPRO_OUT/$STEP_NAME"
WORKING_CONFIG="$ARTIFACTS_DIR/config.json"
rm -rf "$ARTIFACTS_DIR"
mkdir -p "$ARTIFACTS_DIR"
CONFIG_TEMPLATE="${CONFIG_TEMPLATE:-${DEFAULT_CONFIG_TEMPLATE:?engine shim must export DEFAULT_CONFIG_TEMPLATE}}"
"$LIB_SCRIPTS/render-config.sh" "$CONFIG_TEMPLATE" "$WORKING_CONFIG"

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
    ${limit[@]+"${limit[@]}"} "$LIB_SCRIPTS/run-protocol-cmd.sh" "$cmd" "$cmd" \
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
            REPRO_OUT="$side_artifacts" "$LIB_SCRIPTS/run-protocol-cmd.sh" \
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
            "$LIB_SCRIPTS/make-catalog.sh" "$disc_dir" "$catalog_out"
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
      "$ENGINE_SCRIPTS_DIR/reset-databases.sh"
      apply_fixtures
      "$LIB_SCRIPTS/render-config.sh" "$CONFIG_TEMPLATE" "$WORKING_CONFIG"
      ;;
    backend)
      echo "[run] --reset=backend: recreating the backend container" >&2
      "$STOP_BACKEND"
      "$ENGINE_SCRIPTS_DIR/start-backend.sh"
      apply_fixtures
      # Backend recreation may have assigned a new bridge IP.
      "$LIB_SCRIPTS/render-config.sh" "$CONFIG_TEMPLATE" "$WORKING_CONFIG"
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

# The artifact directory for one protocol command on the target side.
# Under --reset=fixture|backend the split is at
# $ARTIFACTS_DIR/{control,target}/<cmd>/; under airbyte-ops's comparison
# mode it's at $ARTIFACTS_DIR/<cmd>/{control,target}/; under
# single-version there's no split. target_read_dir stays as a thin
# convenience for the read-scoped assertions (--min-records / --min-states).
target_command_dir() {
  local cmd="$1"
  if [[ "$PER_IMAGE_SWEEPS" == true ]]; then
    echo "$ARTIFACTS_DIR/target/$cmd"
  elif [[ -d "$ARTIFACTS_DIR/$cmd/target" ]]; then
    echo "$ARTIFACTS_DIR/$cmd/target"
  else
    echo "$ARTIFACTS_DIR/$cmd"
  fi
}
target_read_dir() { target_command_dir read; }

# Split a `[<command>:]<channel>:<regex>[:N]` spec into four lines:
# command, channel, regex, count. The command prefix is optional and
# defaults to `read`. Because <command> ∈ {spec,check,discover,read}
# and <channel> ∈ {stdout,stderr,any} don't overlap, disambiguation is
# purely on the first colon-separated field. Count defaults to 1 unless
# the last colon-separated field parses as a positive integer, in
# which case it is stripped off. This lets a regex contain colons —
# only a trailing `:N` is claimed, and only leading `<command>:` /
# `<channel>:` prefixes are recognized.
parse_match_spec() {
  local spec="$1"
  local first_colon="${spec%%:*}"
  local command=read
  case "$first_colon" in
    spec|check|discover|read)
      command="$first_colon"
      spec="${spec#*:}"
      first_colon="${spec%%:*}"
      ;;
  esac
  case "$first_colon" in
    stdout|stderr|any) ;;
    *)
      echo "[run] --expect-match / --forbid-match first field must be a channel (stdout|stderr|any) or a command (spec|check|discover|read) followed by a channel — got '$first_colon' in '$1'" >&2
      return 2
      ;;
  esac
  local rest="${spec#*:}"
  local regex="$rest" count=1
  if [[ "$rest" =~ ^(.+):([1-9][0-9]*)$ ]]; then
    regex="${BASH_REMATCH[1]}"
    count="${BASH_REMATCH[2]}"
  fi
  printf '%s\n%s\n%s\n%d\n' "$command" "$first_colon" "$regex" "$count"
}

# Count occurrences of a regex against a command's target-side artifacts.
# grep -c returns 1 (with count 0) when nothing matches, which set -e
# would abort on — hence the `|| true`.
count_matches_in_channel() {
  local channel="$1" regex="$2" cmd_dir="$3" total=0 count
  local -a files=()
  case "$channel" in
    stdout) files=("$cmd_dir/stdout.txt") ;;
    stderr) files=("$cmd_dir/stderr.txt") ;;
    any)    files=("$cmd_dir/stdout.txt" "$cmd_dir/stderr.txt") ;;
  esac
  for f in "${files[@]}"; do
    [[ -f "$f" ]] || continue
    count="$(grep -cE -- "$regex" "$f" 2>/dev/null || true)"
    total=$((total + count))
  done
  echo "$total"
}

# Overall verdict for one side: pass iff every executed command's
# STATUS is `pass`. A missing STATUS entry counts as pass because that
# command was not requested (e.g. --command=read never touched spec).
side_all_passed() {
  local prefix="$1" cmd status
  for cmd in spec check discover read; do
    status="${STATUS[${prefix:+${prefix}.}$cmd]:-pass}"
    [[ "$status" == pass ]] || { echo false; return; }
  done
  echo true
}

apply_expectations() {
  local read_dir target_pass control_pass
  read_dir="$(target_read_dir)"

  if [[ -n "$EXPECT_TEST" ]]; then
    if [[ "$PER_IMAGE_SWEEPS" == true ]]; then
      target_pass="$(side_all_passed target)"
    else
      target_pass="$(side_all_passed '')"
    fi
    local want=true
    [[ "$EXPECT_TEST" == fail ]] && want=false
    if [[ "$target_pass" != "$want" ]]; then
      EXPECTATION_FAILURES+=("--expect-test=$EXPECT_TEST (target actually ${target_pass})")
    fi
  fi

  if [[ -n "$EXPECT_CONTROL" ]]; then
    control_pass="$(side_all_passed control)"
    local want=true
    [[ "$EXPECT_CONTROL" == fail ]] && want=false
    if [[ "$control_pass" != "$want" ]]; then
      EXPECTATION_FAILURES+=("--expect-control=$EXPECT_CONTROL (control actually ${control_pass})")
    fi
  fi

  if (( MIN_RECORDS >= 0 )); then
    local records=0
    if [[ -f "$read_dir/stdout.txt" ]]; then
      records="$(grep -cE '"type":\s*"RECORD"' "$read_dir/stdout.txt" 2>/dev/null || true)"
    fi
    if (( records < MIN_RECORDS )); then
      EXPECTATION_FAILURES+=("--min-records=$MIN_RECORDS (got $records)")
    fi
  fi
  if (( MIN_STATES >= 0 )); then
    local states=0
    if [[ -f "$read_dir/stdout.txt" ]]; then
      states="$(grep -cE '"type":\s*"STATE"' "$read_dir/stdout.txt" 2>/dev/null || true)"
    fi
    if (( states < MIN_STATES )); then
      EXPECTATION_FAILURES+=("--min-states=$MIN_STATES (got $states)")
    fi
  fi

  local spec command channel regex count actual parsed cmd_dir
  for spec in ${EXPECT_MATCHES[@]+"${EXPECT_MATCHES[@]}"}; do
    parsed="$(parse_match_spec "$spec")" || exit $?
    { read -r command; read -r channel; read -r regex; read -r count; } <<<"$parsed"
    cmd_dir="$(target_command_dir "$command")"
    actual="$(count_matches_in_channel "$channel" "$regex" "$cmd_dir")"
    if (( actual < count )); then
      EXPECTATION_FAILURES+=("--expect-match=$spec (got $actual of $count required in $command)")
    fi
  done
  for spec in ${FORBID_MATCHES[@]+"${FORBID_MATCHES[@]}"}; do
    parsed="$(parse_match_spec "$spec")" || exit $?
    { read -r command; read -r channel; read -r regex; read -r _count; } <<<"$parsed"
    cmd_dir="$(target_command_dir "$command")"
    actual="$(count_matches_in_channel "$channel" "$regex" "$cmd_dir")"
    if (( actual > 0 )); then
      EXPECTATION_FAILURES+=("--forbid-match=$spec (matched $actual times in $command)")
    fi
  done
}

apply_expectations

# "Determine Final Status" plus "Write Summary Table": one line per
# command, every non-pass rendered as a failure, and the infrastructure
# failures called out separately so a broken run is never read as a
# regression.
INTERNAL_FAILURE=false
ALL_PASSED=true
(( ${#EXPECTATION_FAILURES[@]} > 0 )) && ALL_PASSED=false

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
  local key="$1" status="${STATUS[$1]:-}" expected=""
  if [[ "$PER_IMAGE_SWEEPS" == true ]]; then
    case "$key" in
      control.*) expected="$EXPECT_CONTROL" ;;
      target.*)  expected="$EXPECT_TEST" ;;
    esac
  else
    expected="$EXPECT_TEST"
  fi
  case "$status" in
    fail)     [[ "$expected" == fail ]] || ALL_PASSED=false ;;
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

if (( ${#EXPECTATION_FAILURES[@]} > 0 )); then
  SUMMARY+="

**Expectation failures:**"
  for fail in "${EXPECTATION_FAILURES[@]}"; do
    SUMMARY+="
- $fail"
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
  printf "## \`%s\` regression sweep\n\n%s\n" "$CONNECTOR" "$SUMMARY" \
    >> "$GITHUB_STEP_SUMMARY"
fi

if [[ "$INTERNAL_FAILURE" == true ]]; then
  echo "[run] infrastructure failure — the verdict above is not a test result" >&2
fi

# Expectation failures are exit-1 regardless of the command-level
# verdicts, otherwise a `--expect-test=fail --expect-match=…` case
# whose target correctly exited non-zero would leak that non-zero
# exit as our own — hiding whether the expectations actually matched.
if (( ${#EXPECTATION_FAILURES[@]} > 0 )); then
  exit 1
fi

# A single-command run keeps returning the connector's own exit code, so
# repro scripts can assert on it; a sweep has more than one, so it
# reports pass/fail like the workflow's job status. In per-image mode a
# single-command run is still a single logical command that was executed
# on both sides — surface the target's exit code, which is the fix under
# test.
if [[ "$SINGLE_COMMAND" == true ]]; then
  single_key="${COMMANDS[0]}"
  [[ "$PER_IMAGE_SWEEPS" == true ]] && single_key="target.$single_key"
  if [[ "$EXPECT_TEST" == fail && "${STATUS[$single_key]:-}" == fail ]]; then
    exit 0
  fi
  if [[ "$PER_IMAGE_SWEEPS" == true ]]; then
    exit "${RC["target.${COMMANDS[0]}"]:-1}"
  fi
  exit "${RC[${COMMANDS[0]}]:-1}"
fi
[[ "$ALL_PASSED" == true ]] || exit 1
exit 0

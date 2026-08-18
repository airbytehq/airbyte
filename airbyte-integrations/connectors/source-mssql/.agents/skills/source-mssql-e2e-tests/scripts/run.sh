#!/usr/bin/env bash
# One-shot entrypoint for the source-mssql e2e harness.
#
# Runs the whole sequence — start backend, apply fixtures, render config,
# derive a configured catalog, run the protocol command, tear down — so a
# prove-fix run is a single command instead of five ordered ones, and so
# CI can invoke the same sequence the agent runs locally.
#
# Usage:
#   run.sh [--command=read] [--fixture=PATH]… [--test-version=dev]
#          [--control-version=TAG] [--step-name=NAME] [--catalog=PATH]
#          [--sync-mode=full_refresh|incremental] [--cursor-field=NAME]
#          [--streams=a,b] [--config-template=PATH] [--build] [--keep-backend]
#          [-- extra airbyte-ops args…]
#
# Defaults reproduce the documented prove-fix flow: `read` against
# airbyte/source-mssql:dev using fixtures/sql/00-init-base.sql and
# fixtures/configs/base.template.json.
#
# Passing --control-version switches airbyte-ops into comparison mode and
# emits the side-by-side SPEC/CHECK/DISCOVER/READ diff that Path B of the
# prove_fix playbook reports as evidence.
#
# Exit code is the connector's own exit code, not the CLI's.
#
# Env: REPRO_OUT, BACKEND_NAME, BACKEND_SA_PASSWORD, BACKEND_PORT,
#      AIRBYTE_OPS (see SKILL.md)
set -euo pipefail

SKILL_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SCRIPTS="$SKILL_DIR/scripts"
CONNECTOR="source-mssql"
REPRO_OUT="${REPRO_OUT:-/tmp/$CONNECTOR-repro}"
export REPRO_OUT

COMMAND="read"
FIXTURES=()
TEST_VERSION="dev"
CONTROL_VERSION_ARG=""
STEP_NAME=""
CATALOG=""
SYNC_MODE="full_refresh"
CURSOR_FIELD=""
STREAMS=""
CONFIG_TEMPLATE="$SKILL_DIR/fixtures/configs/base.template.json"
BUILD=false
KEEP_BACKEND=false
EXTRA_ARGS=()

while [[ $# -gt 0 ]]; do
  case "$1" in
    --command=*)         COMMAND="${1#*=}" ;;
    --fixture=*)         FIXTURES+=("${1#*=}") ;;
    --test-version=*)    TEST_VERSION="${1#*=}" ;;
    --control-version=*) CONTROL_VERSION_ARG="${1#*=}" ;;
    --step-name=*)       STEP_NAME="${1#*=}" ;;
    --catalog=*)         CATALOG="${1#*=}" ;;
    --sync-mode=*)       SYNC_MODE="${1#*=}" ;;
    --cursor-field=*)    CURSOR_FIELD="${1#*=}" ;;
    --streams=*)         STREAMS="${1#*=}" ;;
    --config-template=*) CONFIG_TEMPLATE="${1#*=}" ;;
    --build)             BUILD=true ;;
    --keep-backend)      KEEP_BACKEND=true ;;
    --)                  shift; EXTRA_ARGS=("$@"); break ;;
    -h|--help)           sed -n '2,27p' "${BASH_SOURCE[0]}"; exit 0 ;;
    *) echo "[run] unknown argument: $1" >&2; exit 2 ;;
  esac
  shift
done

case "$COMMAND" in
  spec|check|discover|read) ;;
  *) echo "[run] --command must be spec|check|discover|read (got '$COMMAND')" >&2; exit 2 ;;
esac
if [[ ${#FIXTURES[@]} -eq 0 ]]; then
  FIXTURES=("$SKILL_DIR/fixtures/sql/00-init-base.sql")
fi
if [[ -z "$STEP_NAME" ]]; then
  STEP_NAME="$COMMAND-$TEST_VERSION${CONTROL_VERSION_ARG:+-vs-$CONTROL_VERSION_ARG}"
fi

# The harness pulls published control tags itself but cannot build :dev.
if [[ "$TEST_VERSION" == "dev" ]] && { [[ "$BUILD" == true ]] \
  || ! docker image inspect "airbyte/$CONNECTOR:dev" >/dev/null 2>&1; }; then
  REPO_ROOT="$(git -C "$SKILL_DIR" rev-parse --show-toplevel)"
  echo "[run] building airbyte/$CONNECTOR:dev from the current checkout" >&2
  "$REPO_ROOT/gradlew" ":airbyte-integrations:connectors:$CONNECTOR:airbyteDocker" \
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

"$SCRIPTS/start-backend.sh"
for fixture in "${FIXTURES[@]}"; do
  "$SCRIPTS/apply-sql.sh" "$fixture"
done

WORKING_CONFIG="$REPRO_OUT/working/$STEP_NAME.config.json"
"$SCRIPTS/render-config.sh" "$CONFIG_TEMPLATE" "$WORKING_CONFIG"

CMD_ARGS=("--config-path=$WORKING_CONFIG")

if [[ "$COMMAND" == "read" ]]; then
  if [[ -z "$CATALOG" ]]; then
    # Derive the configured catalog from a real discover rather than
    # relying on a hand-written one that can drift from the fixture. In
    # comparison mode both images read the same catalog, so discover with
    # the control: a catalog the older image accepts is also accepted by
    # the target, but not necessarily the reverse.
    set +e
    "$SCRIPTS/run-protocol-cmd.sh" discover "$STEP_NAME-catalog-discover" \
      "${CONTROL_VERSION_ARG:-$TEST_VERSION}" "--config-path=$WORKING_CONFIG"
    DISCOVER_RC=$?
    set -e
    if (( DISCOVER_RC != 0 )); then
      echo "[run] catalog discover failed (exit $DISCOVER_RC); see" \
        "$REPRO_OUT/$STEP_NAME-catalog-discover" >&2
      exit "$DISCOVER_RC"
    fi
    CATALOG="$REPRO_OUT/working/$STEP_NAME.catalog.json"
    STREAMS="$STREAMS" SYNC_MODE="$SYNC_MODE" CURSOR_FIELD="$CURSOR_FIELD" \
      "$SCRIPTS/make-catalog.sh" "$REPRO_OUT/$STEP_NAME-catalog-discover" "$CATALOG"
  fi
  CMD_ARGS+=("--catalog-path=$CATALOG")
fi
if [[ "$COMMAND" == "spec" ]]; then
  CMD_ARGS=()
fi

set +e
CONTROL_VERSION="$CONTROL_VERSION_ARG" \
  "$SCRIPTS/run-protocol-cmd.sh" "$COMMAND" "$STEP_NAME" "$TEST_VERSION" \
  ${CMD_ARGS[@]+"${CMD_ARGS[@]}"} ${EXTRA_ARGS[@]+"${EXTRA_ARGS[@]}"}
RC=$?
set -e

echo "[run] connector exit code: $RC" >&2
echo "[run] artifacts: $REPRO_OUT/$STEP_NAME" >&2
exit "$RC"

#!/usr/bin/env bash
# Run an Airbyte protocol command against airbyte/source-mssql:<version>
# via `airbyte-ops cloud connector regression-test --skip-compare=True`.
#
# Usage:  run-protocol-cmd.sh <command> <step-name> <version> [extra-args…]
#
#   <command>     spec | check | discover | read
#   <step-name>   subdirectory under $REPRO_OUT to write artifacts to
#   <version>     image tag, e.g. 4.4.2 / 4.3.4 / dev / latest
#   [extra-args]  any additional flags forwarded verbatim
#
# Output:
#   $REPRO_OUT/<step-name>/stdout.txt
#   $REPRO_OUT/<step-name>/stderr.txt
#   $REPRO_OUT/<step-name>/result.json   (small summary)
#
# Env:
#   REPRO_OUT     parent output directory (default: /tmp/source-mssql-repro)
#   AIRBYTE_OPS   command to invoke airbyte-ops. Default picks the binary
#                 on $PATH (`airbyte-ops`) if `uv tool install
#                 airbyte-internal-ops` was run, else falls back to
#                 `uvx airbyte-internal-ops`.
set -euo pipefail

REPRO_OUT="${REPRO_OUT:-/tmp/source-mssql-repro}"
if [[ -z "${AIRBYTE_OPS:-}" ]]; then
  if command -v airbyte-ops >/dev/null 2>&1; then
    AIRBYTE_OPS="airbyte-ops"
  else
    AIRBYTE_OPS="uvx airbyte-internal-ops"
  fi
fi

if [[ $# -lt 3 ]]; then
  echo "usage: $(basename "$0") <command> <step-name> <version> [extra-args…]" >&2
  exit 2
fi
COMMAND="$1"; shift
STEP_NAME="$1"; shift
VERSION="$1"; shift

OUT_DIR="$REPRO_OUT/$STEP_NAME"
rm -rf "$OUT_DIR"
mkdir -p "$OUT_DIR"

# `airbyte-ops cloud connector regression-test` in single-version mode
# prints "Error: Single-version regression test failed …" when the
# underlying connector exits non-zero, but the CLI itself returns 0.
# Run it with `set +e` so a non-zero CLI exit also doesn't abort the
# script, then derive the connector's actual exit code from
# `report.md` so the caller's `RC` is meaningful.
set +e
# shellcheck disable=SC2086
$AIRBYTE_OPS cloud connector regression-test \
  --skip-compare=True \
  --command="$COMMAND" \
  --test-image="airbyte/source-mssql:$VERSION" \
  --output-dir="$OUT_DIR" \
  "$@"
set -e

CONNECTOR_RC="$(
  grep -E '^- \*\*Exit Code:\*\*' "$OUT_DIR/report.md" 2>/dev/null \
    | head -n 1 \
    | grep -oE '[0-9]+' \
    | head -n 1
)"
exit "${CONNECTOR_RC:-1}"

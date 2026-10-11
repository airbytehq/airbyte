#!/usr/bin/env bash
set -euo pipefail

if [[ $# -lt 1 || ! -f "$1" ]]; then
  echo "usage: $(basename "$0") <path/to/file.sql>" >&2
  exit 2
fi
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
"$SCRIPT_DIR/sf.py" exec-file "$1" --schema "$PROVEFIX_SCHEMA"

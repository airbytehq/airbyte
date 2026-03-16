#!/usr/bin/env bash
# Create .venv if missing, install deps, run validate_onelake_config.py (with --connectivity by default).
set -e
cd "$(dirname "$0")/.."
VENV=".venv"
REQ="scripts/requirements-validate.txt"

if [[ ! -d "$VENV" ]]; then
  echo "Creating virtualenv at $VENV ..."
  python3 -m venv "$VENV"
fi
echo "Installing/updating deps from $REQ ..."
"$VENV/bin/pip" install -q -r "$REQ"
echo "Running validation and connectivity test ..."
exec "$VENV/bin/python" scripts/validate_onelake_config.py "$@" --connectivity

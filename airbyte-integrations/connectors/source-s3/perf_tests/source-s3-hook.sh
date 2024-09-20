#!/bin/bash

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PYTHON_EXEC="$SCRIPT_DIR/../.venv/bin/python"

"$PYTHON_EXEC" -m source_s3.run "$@"

#!/bin/bash

# This script is used to run the source-s3 connector with the local editable
# poetry environment. It is called by performance test script.

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PYTHON_EXEC="$SCRIPT_DIR/../.venv/bin/python"

"$PYTHON_EXEC" -m source_s3.run "$@"

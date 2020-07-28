#!/bin/bash
# Use python 3.7 to guarantee compatibility with deps

VENV=$1
PIP_PACKAGE_NAME=${2:-$VENV}

virtualenv -p python3.7 "$VENV"
source "${VENV}"/bin/activate
pip install "$PIP_PACKAGE_NAME"


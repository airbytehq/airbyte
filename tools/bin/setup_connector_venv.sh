#!/usr/bin/env bash

set -e

CONNECTOR=$1
PYTHON_EXECUTABLE=${2-python}
echo Installing requirements for $CONNECTOR

cd airbyte-integrations/connectors/$CONNECTOR
$PYTHON_EXECUTABLE -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
pip install '.[tests]'
pip install pytest-cov

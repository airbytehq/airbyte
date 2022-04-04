#!/usr/bin/env bash

set -e

CONNECTOR=$1
echo Installing requirements for $CONNECTOR

cd airbyte-integrations/connectors/$CONNECTOR
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
pip install '.[tests]'
pip install pytest-cov

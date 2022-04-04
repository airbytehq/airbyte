#!/usr/bin/env bash

set -e

CONNECTOR=$1

cd airbyte-integrations/connectors/$CONNECTOR
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
pip install '.[tests]'
pip install pytest-cov
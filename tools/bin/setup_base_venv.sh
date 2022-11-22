#!/usr/bin/env bash

set -e

PYTHON_EXECUTABLE=${1-python}
echo Creating $PYTHON_EXECUTABLE virtualenv

$PYTHON_EXECUTABLE -m venv --without-pip .venv
source .venv/bin/activate
python get-pip.py
for base in base-normalization base-python base-python-test source-acceptance-test base-singer airbyte-protocol
do
  $PYTHON_EXECUTABLE -m venv --without-pip airbyte-integrations/bases/$base/.venv
  source airbyte-integrations/bases/$base/.venv/bin/activate
  python get-pip.py
done
cd airbyte-integrations/connectors/$CONNECTOR

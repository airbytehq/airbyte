#!/usr/bin/env bash

set -e

PYTHON_EXECUTABLE=${1-python}
echo Creating $PYTHON_EXECUTABLE virtualenv

$PYTHON_EXECUTABLE -m venv --without-pip .venv
source .venv/bin/activate
python get-pip.py
for base in base-normalization base-python base-python-test source-acceptance-test base-singer airbyte-protocol
do
  ln -s $(pwd)/.venv airbyte-integrations/bases/$base/
done
cd airbyte-integrations/connectors/$CONNECTOR

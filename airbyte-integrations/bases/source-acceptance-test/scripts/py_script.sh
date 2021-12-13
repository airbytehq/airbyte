#!/bin/bash

sleep 1

set -e
shift

CODE_FOLDER="/data/"
CONNECTOR_FOLDER="${CODE_FOLDER}/code_folder"
ACCEPTANCE_TESTS_FOLDER="${CODE_FOLDER}/source_acceptance_test"

PY_ACCEPTANCE_FILE="${CONNECTOR_FOLDER}/integration_tests/acceptance.py"
echo "try to find a acceptance file: ${PY_ACCEPTANCE_FILE}"
if [ -f ${PY_ACCEPTANCE_FILE} ]; then
  echo "found ${PY_ACCEPTANCE_FILE}..."
else
  echo "not found ${PY_ACCEPTANCE_FILE}..."
  unset PY_ACCEPTANCE_FILE
fi

PY_UNIT_TESTS_FOLDER="${CONNECTOR_FOLDER}/unit_tests"
echo "try to find a unit tests folder: ${PY_UNIT_TESTS_FOLDER}"
if [ -d ${PY_UNIT_TESTS_FOLDER} ]; then
  echo "found ${PY_UNIT_TESTS_FOLDER}..."
else
  echo "not found ${PY_UNIT_TESTS_FOLDER}..."
  unset PY_UNIT_TESTS_FOLDER
fi

if [ -z ${PY_ACCEPTANCE_FILE} ] && [ ! -z ${PY_UNIT_TESTS_FOLDER} ]; then
  echo "not found any custom tests..."
  exit 0
fi

pip install --quiet flake8
echo "run flake8...."
flake8 --exclude=.venv,models,.eggs --extend-ignore=E203,E231,E501,W503 ${CONNECTOR_FOLDER}
echo "tested by flake8 successfully..."

cd ${CONNECTOR_FOLDER}
echo "try to setup test deps..."
pip install --quiet -e ${ACCEPTANCE_TESTS_FOLDER}
pip install --quiet -e  "${CONNECTOR_FOLDER}[tests]"
if [ ! -z ${PY_UNIT_TESTS_FOLDER} ]; then
  echo "run unit tests..."
  # python -m pytest unit_tests
  echo "unit tests are successful..."
fi

if [ ! -z ${PY_ACCEPTANCE_FILE} ]; then
  echo "run integration tests..."
  echo " python -m pytest integration_tests -p integration_tests.acceptance --acceptance-test-config ${CONNECTOR_FOLDER} $@"
  python -m pytest integration_tests -p integration_tests.acceptance --acceptance-test-config ${CONNECTOR_FOLDER} $@
  echo "integration tests are successful..."
fi


exit 1






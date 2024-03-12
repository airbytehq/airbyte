#!/bin/bash

set -e

# installReqs
echo "Installing dependencies..."
pip install ".[dev,tests]"
pip install ".[main]"
echo "Done installing dependencies."

# more dev dependencies! from build.gradle
# TODO: move these to setup.py/poetry
pip install pip==23.2.1
pip install mccabe==0.6.1
# https://github.com/csachs/pyproject-flake8/issues/13
pip install flake8==4.0.1
# flake8 doesn't support pyproject.toml files
# and thus there is the wrapper "pyproject-flake8" for this
pip install pyproject-flake8==0.0.1a2
pip install pytest==6.2.5
pip install coverage[toml]==6.3.1

# flakeCheck
echo "Running flake check..."
pflake8 --config pyproject.toml ./
echo "Done running flake check."

# test
# install test reqs
# pip install ".[tests]"
# We already did this but putting everything in order for due diligence right now

# run tests
echo "Running unit tests and coverage checks..."
coverage run --data-file=unit_tests/.coverage.testPython --rcfile=pyproject.toml -m pytest -s unit_tests -c pytest.ini
echo "Done running unit tests."

# Probably very old tests for _all_ low code connectors

#echo "Validating yaml schema for low code connectors..."
#bin/validate-yaml-schema.sh
#echo "Done validating yaml schema."

#echo "Running unit tests for low code connectors..."
#bin/low-code-unit-tests.sh
#echo "Done running unit tests for low code connectors."

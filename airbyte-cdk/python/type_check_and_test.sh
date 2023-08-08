#!/bin/bash

# TODO(davin): Migrate to Gradle?
# TODO(davin): This should not assume the user has already set up the venv folder.

# Static Type Checking
echo "Running MyPy to static check and test files."
mypy airbyte_cdk/ unit_tests/ --config mypy.ini

printf "\n"

# Test with Coverage Report
echo "Running tests.."
# The -s flag instructs PyTest to capture stdout logging; simplifying debugging.
pytest -s -vv --cov=airbyte_cdk unit_tests/

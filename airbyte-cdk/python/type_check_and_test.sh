#!/bin/bash

# TODO(davin): Migrate to Gradle?
# TODO(davin): This should not assume the user has already set up the venv folder.

# Static Type Checking
echo "Running MyPy to static check base_python directory and test files."
mypy airbyte_cdk/base_python unit_tests

printf "\n"

# Test with Coverage Report
echo "Running tests.."
pytest --cov=airbyte_cdk unit_tests/

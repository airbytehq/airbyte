#!/bin/bash
# Runs the CI sript for the Java CDK.
#
# Usage:
#  ./ci.sh --help
#  ./ci.sh build
#  ./ci.sh ci
#  ./ci.sh test

CMD="aircmd cdk java $@"
REPO_ROOT="$(git rev-parse --show-toplevel)"
CI_DIR=$REPO_ROOT/airbyte-ci/connectors/cdk

# Install pipx if missing
if ! command -v pipx &> /dev/null
then
    echo "Installing pipx..."
    python3 -m pip install --user pipx
    pipx ensurepath
fi

# Install poetry if missing
if ! command -v poetry &> /dev/null
then
    echo "Installing poetry..."
    pipx install poetry
fi

# Install poetry project if needed
poetry install --directory $CI_DIR

# Run the CI script
poetry run --directory $CI_DIR $CMD

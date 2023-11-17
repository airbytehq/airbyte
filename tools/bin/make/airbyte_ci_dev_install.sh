#!/usr/bin/env bash
set -o errexit -o nounset -o pipefail

# Check if pyenv is installed, and install it if not
if ! which pyenv >/dev/null; then
    echo "pyenv not found, installing pyenv..."
    brew install pyenv
    echo "pyenv installed."
else
    echo "pyenv is already installed."
fi

# Check if pipx is installed, and install it if not
if ! which pipx >/dev/null; then
    echo "pipx not found, installing pipx..."
    python -m pip install --user pipx
    python -m pipx ensurepath
    echo "pipx installed."
else
    echo "pipx is already installed."
fi

# Install airbyte-ci development version
pipx install --editable --force --python=python3.10 airbyte-ci/connectors/pipelines/
echo "Development version of airbyte-ci installed."

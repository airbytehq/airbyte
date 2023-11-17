#!/usr/bin/env bash
set -o errexit -o nounset -o pipefail

# Check if Python 3.10 is on the path
if ! which python3.10 >/dev/null; then
  echo "python3.10 not found on the path."
  echo "Please install Python 3.10 using pyenv:"
  echo "1. Install pyenv if not already installed:"
  echo "   brew install pyenv"
  echo "2. Install Python 3.10 using pyenv:"
  echo "   pyenv install 3.10.12"
  exit 1
else
  echo "Python 3.10 is already installed."
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

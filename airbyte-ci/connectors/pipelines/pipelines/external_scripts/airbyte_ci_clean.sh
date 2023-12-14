#!/usr/bin/env bash
set -o errexit -o nounset -o pipefail

# Check if pipx is on the path and if so, uninstall pipelines
if which pipx >/dev/null 2>&1; then
    # ignore errors if pipelines is not installed
    pipx uninstall pipelines || true
    echo "Uninstalled pipelines via pipx"
else
    echo "pipx not found, skipping uninstall of pipelines"
fi

# Remove airbyte-ci if it's on the path
while which airbyte-ci >/dev/null 2>&1; do
    echo "Removing $(which airbyte-ci)"
    rm "$(which airbyte-ci)"
done
echo "Removed airbyte-ci"

# Remove airbyte-ci-internal if it's on the path
while which airbyte-ci-internal >/dev/null 2>&1; do
    echo "Removing $(which airbyte-ci)"
    rm "$(which airbyte-ci-internal)"
done
echo "Removed airbyte-ci-internal"

# Remove airbyte-ci-dev if it's on the path
while which airbyte-ci-dev >/dev/null 2>&1; do
    echo "Removing $(which airbyte-ci)"
    rm "$(which airbyte-ci-dev)"
done
  echo "Removed airbyte-ci-dev"

# Check if airbyte-ci is stashed away in pyenv
# If so, remove it
# This prevents `pyenv init -` from adding it back to the path
while pyenv whence --path airbyte-ci >/dev/null 2>&1; do
    rm "$(pyenv whence --path airbyte-ci)"
    echo "Uninstalled pipelines via pyenv"
done
    echo "All airbyte-ci references removed from pyenv versions."

echo "Cleanup of airbyte-ci install completed."

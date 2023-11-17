#!/usr/bin/env bash
set -o errexit -o nounset -o pipefail

# Check if pipx is on the path and if so, uninstall pipelines
if which pipx >/dev/null 2>&1; then
    pipx uninstall pipelines
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

echo "Cleanup completed."
echo ""
echo "Please run 'make tools.airbyte-ci.install' to install airbyte-ci again"


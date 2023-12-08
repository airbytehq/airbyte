#!/usr/bin/env bash
set -o errexit -o nounset -o pipefail

echo "Checking if airbyte-ci is correctly installed..."

# Check that airbyte-ci is on the PATH
# If not print an error message and exit
if ! which airbyte-ci >/dev/null 2>&1; then
    echo "airbyte-ci is not on the PATH"
    echo "Check that \$HOME/.local/bin is part of the PATH"
    echo ""
    echo "If not, please add 'export PATH=\"\$HOME/.local/bin:\$PATH\"' to your shell profile"
    exit 1
fi

EXPECTED_PATH="$HOME/.local/bin/airbyte-ci"
AIRBYTE_CI_PATH=$(which airbyte-ci 2>/dev/null)
if [ "$AIRBYTE_CI_PATH" != "$EXPECTED_PATH" ]; then
    echo "airbyte-ci is not from the expected install location: $EXPECTED_PATH"
    echo "airbyte-ci is installed at: $AIRBYTE_CI_PATH"
    echo "Check that airbyte-ci exists at \$HOME/.local/bin and \$HOME/.local/bin is part of the PATH"
    echo ""
    echo "If it is, try running 'make tools.airbyte-ci.clean', then run 'make tools.airbyte-ci.install' again"
    exit 1
fi

# Check if the AIRBYTE_CI_PATH is a symlink
if [ -L "$AIRBYTE_CI_PATH" ]; then
    echo ""
    echo "#########################################################################"
    echo "#                                                                       #"
    echo "#  Warning: airbyte-ci at $AIRBYTE_CI_PATH is a symlink.                #"
    echo "#  You are possibly using a development version of airbyte-ci.          #"
    echo "#  To update to a release version, run 'make tools.airbyte-ci.install'  #"
    echo "#                                                                       #"
    echo "#  If this warning persists, try running 'make tools.airbyte-ci.clean'  #"
    echo "#  Then run 'make tools.airbyte-ci.install' again.                      #"
    echo "#                                                                       #"
    echo "#########################################################################"
    echo ""
fi

echo "airbyte-ci is correctly installed at $EXPECTED_PATH"

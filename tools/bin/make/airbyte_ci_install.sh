#!/usr/bin/env bash
set -o errexit -o nounset -o pipefail

# Base URL for downloading airbyte-ci
RELEASE_URL=${RELEASE_URL:-"https://connectors.airbyte.com/files/airbyte-ci/releases"}

# Determine the operating system and download the binary
OS=$(uname)
VERSION=${1:-latest}


if [ "$OS" = "Linux" ]; then
    URL="${RELEASE_URL}/ubuntu/${VERSION}/airbyte-ci"
    echo "Linux based system detected. Downloading from $URL"
elif [ "$OS" = "Darwin" ]; then
    URL="${RELEASE_URL}/macos/${VERSION}/airbyte-ci"
    echo "macOS based system detected. Downloading from $URL"
else
    echo "Unsupported operating system"
    exit 1
fi

# Create the directory if it does not exist
mkdir -p ~/.local/bin

# Remove the old binary if it exists
rm -f ~/.local/bin/airbyte-ci

# Download the binary
curl -L -f "$URL" -o ~/.local/bin/airbyte-ci

# Make the binary executable
chmod +x ~/.local/bin/airbyte-ci

echo ""
echo "╔───────────────────────────────────────────────────────────────────────────────╗"
echo "│                                                                               │"
echo "│    AAA   IIIII RRRRRR  BBBBB   YY   YY TTTTTTT EEEEEEE         CCCCC  IIIII   │"
echo "│   AAAAA   III  RR   RR BB   B  YY   YY   TTT   EE             CC       III    │"
echo "│  AA   AA  III  RRRRRR  BBBBBB   YYYYY    TTT   EEEEE   _____  CC       III    │"
echo "│  AAAAAAA  III  RR  RR  BB   BB   YYY     TTT   EE             CC       III    │"
echo "│  AA   AA IIIII RR   RR BBBBBB    YYY     TTT   EEEEEEE         CCCCC  IIIII   │"
echo "│                                                                               │"
echo "│  === Installation complete ===                                                │"
echo "╚───────────────────────────────────────────────────────────────────────────────╝"
echo ""


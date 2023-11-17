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

# Download the binary to a temporary folder
TMP_DIR=$(mktemp -d)
TMP_FILE="$TMP_DIR/airbyte-ci"
curl -L -f "$URL" -o "$TMP_FILE"

# Check if the destination path is a symlink and delete it if it is
if [ -L ~/.local/bin/airbyte-ci ]; then
  rm ~/.local/bin/airbyte-ci
fi

# Copy the file from the temporary folder to the destination
cp "$TMP_FILE" ~/.local/bin/airbyte-ci

# Make the binary executable
chmod +x ~/.local/bin/airbyte-ci

# Clean up the temporary folder
rm -rf "$TMP_DIR"

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


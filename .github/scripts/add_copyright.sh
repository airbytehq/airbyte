#!/bin/bash
set -e

YEAR=$(date +%Y)

if ! command -v addlicense &> /dev/null; then
    echo "Installing addlicense..."
    go install github.com/google/addlicense@latest
    export PATH=$PATH:$(go env GOPATH)/bin
fi

addlicense -c "Airbyte, Inc." -l copyright -v -y "$YEAR" -f .github/scripts/LICENSE_TEMPLATE "$@"

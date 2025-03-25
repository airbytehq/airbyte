#!/bin/bash
YEAR=$(date +%Y)
addlicense -c "Airbyte, Inc." -l copyright -v -y "$YEAR" -f .github/scripts/LICENSE_TEMPLATE "$@"

#!/usr/bin/env bash

set -e

. tools/lib/lib.sh

GIT_REVISION=$(git rev-parse HEAD)
[[ -z "$GIT_REVISION" ]] && echo "Couldn't get the git revision..." && exit 1

echo "**IMPORTANT, only merge if:**"
echo "  - octavia-cli build is passing"
echo "  - The corresponding Bump Airbyte PR was merged"

echo
echo "Changelog:"
echo
PAGER=cat git log v${PREV_VERSION}..${GIT_REVISION} --oneline --decorate=no -- octavia-cli

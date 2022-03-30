#!/usr/bin/env bash

set -e

. tools/lib/lib.sh

GIT_REVISION=$(git rev-parse HEAD)
[[ -z "$GIT_REVISION" ]] && echo "Couldn't get the git revision..." && exit 1

echo "*IMPORTANT: Only merge if the platform build is passing!*"
echo
echo "Changelog:"
echo
PAGER=cat git log v${PREV_VERSION}..${GIT_REVISION} --oneline --decorate=no
echo
echo "Steps After Merging PR:"
echo "1. Merge the Bump octavia PR"
echo "2. Pull most recent version of master"
echo "3. Run ./tools/bin/tag_version.sh"
echo "4. Create a GitHub release with the changelog"

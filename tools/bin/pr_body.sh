#!/usr/bin/env bash

set -e

. tools/lib/lib.sh

[[ -z "$GIT_REVISION" ]] && echo "Couldn't get the git revision..." && exit 1

echo "*IMPORTANT: Only merge if the platform build is passing!*"
echo
# Do not change the following line - the Create Release Github action relies on it
echo "Changelog:"
echo
PAGER=cat git log v${PREV_VERSION}..${GIT_REVISION} --oneline --decorate=no
# The following empty 'echo' is also important for marking the end of the changelog for the Create Release Github action
echo
echo "### Instructions"
echo "1) *SQUASH MERGE* this PR - this is necessary to ensure the automated Create Release action is triggered."
echo "2) Double check that the [Create Release](https://github.com/airbytehq/airbyte/actions/workflows/create-release.yml) action was triggered and ran successfully on the commit to master \
(this should only take a few seconds)."
echo "3) If the Create Release action failed due to a transient issue, retry the action. If it failed due to \
a non-transient issue, create a release manually by following the below instructions."
echo
echo "<details>"
echo "<summary>Create the GitHub release manually</summary>"
echo 
echo "1. Pull most recent version of master"
echo "2. Run ./tools/bin/tag_version.sh"
echo "3. Create a GitHub release with the changelog"
echo "</details>"

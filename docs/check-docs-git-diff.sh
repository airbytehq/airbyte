#!bin/bash
set -eux

# This script checks the status of the documentation files in the docs directory.
# It should return '1' if a build is needed, and '0' if everything is up to date.
#
# This script will be called by Vercel here:
# - https://vercel.com/airbyte-growth/airbyte-docs/settings/git#ignored-build-step

git diff HEAD^ HEAD --quiet . ../docs && git log -n 1 --oneline | grep -Eq "\[(up-to-date|auto-publish)\]" || exit 1

latest_commit_message=$(git log -n 1 --oneline)
if echo "$latest_commit_message" | grep -Eq "\[(up-to-date|auto-publish)\]"; then
    # Both conditions met - no changes and commit has required tag
    echo "✅ Skipping. Commit marked as [up-to-date]/[auto-publish]. ('$latest_commit_message')"
    exit 0
fi

# Check if the docs directories have changed in the latest commit
if git diff HEAD^ HEAD --quiet ./docusaurus ./docs; then
    # If there are no changes, we're good to skip the build.
    echo "✅ No changes in docs paths. Skipping build."
    exit 0
fi

# If we got here, then both of these conditions are true:
# 1. There were changes in the docs or current directory, and
# 2. The commit didn't have one of the tags [up-to-date] or [auto-publish].
echo "❌ Documentation changes detected. Build is requested."
exit 1

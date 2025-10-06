#!/usr/bin/env bash
set -eu

# This script checks the status of the documentation files in the docs directory.
# It should return '1' if a build is needed, and '0' if everything is up to date.
#
# This script will be called by Vercel here:
# - https://vercel.com/airbyte-growth/airbyte-docs/settings/git#ignored-build-step
#
# This script is intended to be run from the root of the Airbyte repository.
#
# Usage:
#   ./docs/check-docs-git-diff.sh                       # Check for any changes in the branch.
#   ./docs/check-docs-git-diff.sh --latest-commit-only  # Only check the latest commit for changes.

# parse flags
LATEST_COMMIT_ONLY=false
while [[ $# -gt 0 ]]; do
  case "$1" in
    --latest-commit-only)
      LATEST_COMMIT_ONLY=true
      echo "⚙️ Running in '--latest-commit-only' mode."
      echo "Only the most recent commit will be checked for changes."
      ;;
    *)
      echo "Unknown argument: $1" >&2;
      exit 1
      ;;
  esac
  shift
done

latest_commit_message=$(git log -n 1 --oneline)
echo "⚙️ Checking for a skip directive in the commit message: ('$latest_commit_message')"
if echo "$latest_commit_message" | grep -Eq "\[(up-to-date|auto-publish)\]"; then
    echo "✅ Skipping. Commit marked as [up-to-date]/[auto-publish]. ('$latest_commit_message')"
    exit 0
fi

REMOTE=origin
DEFAULT_BRANCH=master
COMPARE_TO_REF="${REMOTE}/${DEFAULT_BRANCH}"
if [ "$LATEST_COMMIT_ONLY" == 'true' ]; then
    # We only want to compare the latest commit against the previous one:
    COMPARE_TO_REF="HEAD^"
fi

echo "⚙️ Checking for git changes within the docs paths..."
if git diff "${COMPARE_TO_REF}"...HEAD --quiet ./docusaurus ./docs .markdownlint.jsonc; then
    echo "✅ No changes in docs paths. Skipping build."
    exit 0
fi

# If we got here, then both of these conditions are true:
# 1. There were changes in the docs or current directory, and
# 2. The commit didn't have one of the tags [up-to-date] or [auto-publish].
echo "❌ Documentation changes detected. Build is requested."
exit 1

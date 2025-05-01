#!/usr/bin/env bash

# This script is used to find all modified connector directories in the Airbyte repository.
# It compares the current branch with the default branch and filters out files that match certain ignore patterns.

DEFAULT_BRANCH="master"

# 1) update remote default branch quietly
git fetch --quiet origin $DEFAULT_BRANCH

# 2) set up ignore patterns
ignore_patterns=(
  'README.md'
  '.coveragerc'
)
# join with | into a grouped regex
ignore_globs="($(IFS='|'; echo "${ignore_patterns[*]}"))$"
# 3) collect all file changes
committed=$(git diff --name-only origin/$DEFAULT_BRANCH...HEAD)
staged=$(git diff --cached --name-only)
unstaged=$(git diff --name-only)
untracked=$(git ls-files --others --exclude-standard)

# 4) merge into one list
all_changes=$(printf '%s\n%s\n%s\n%s' "$committed" "$staged" "$unstaged" "$untracked")

# 5) drop ignored files
filtered=$(printf '%s\n' "$all_changes" | grep -v -E "/${ignore_globs}")

# 6) keep only connector paths
connectors=$(printf '%s\n' "$filtered" | grep -E '^airbyte-integrations/connectors/[^/]+' )

# 7) extract just the connector directory name
dirs=$(printf '%s\n' "$connectors" \
  | sed -E 's|airbyte-integrations/connectors/([^/]+).*|\1|'
)

# 8) output sorted, unique list
if [ "$dirs" ]; then
  printf '%s\n' "$dirs" | sort -u
fi

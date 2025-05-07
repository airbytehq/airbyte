#!/usr/bin/env bash

# This script is used to find all modified connector directories in the Airbyte repository.
# It compares the current branch with the default branch and filters out files that match certain ignore patterns.

set -euo pipefail

# 0) Collect arguments
DEFAULT_BRANCH="master"
JAVA=false
NO_JAVA=false

# parse flags
while [[ $# -gt 0 ]]; do
  case "$1" in
    --java|java)      JAVA=true ;;
    --no-java|no-java) NO_JAVA=true ;;
    *) echo "Unknown argument: $1" >&2; exit 1 ;;
  esac
  shift
done

# 1) update remote default branch quietly
git fetch --quiet origin $DEFAULT_BRANCH

# 2) set up ignore patterns
ignore_patterns=(
  '.coveragerc'
  'poe_tasks.toml'
  'README.md'
)
# join with | into a grouped regex
ignore_globs="($(IFS='|'; echo "${ignore_patterns[*]}"))$"

# 3) collect all file changes
committed=$(git diff --name-only origin/"$DEFAULT_BRANCH"...HEAD)
staged=$(git diff --cached --name-only)
unstaged=$(git diff --name-only)
untracked=$(git ls-files --others --exclude-standard)

# 4) merge into one list
all_changes=$(printf '%s\n%s\n%s\n%s' "$committed" "$staged" "$unstaged" "$untracked")

# 5) drop ignored files
filtered=$(printf '%s\n' "$all_changes" | grep -v -E "/${ignore_globs}")

# 6) keep only connector paths
connectors_paths=$(printf '%s\n' "$filtered" | grep -E '^airbyte-integrations/connectors/[^/]+')

# 7) extract just the connector directory name
dirs=$(printf '%s\n' "$connectors_paths" \
  | sed -E 's|airbyte-integrations/connectors/([^/]+).*|\1|' \
)

# 8) unique list of modified connectors
connectors=()
if [ -n "$dirs" ]; then
  while IFS= read -r d; do
    connectors+=("$d")
  done <<< "$(printf '%s\n' "$dirs" | sort -u)"
fi

# if no flags, output all and exit
if ! $JAVA && ! $NO_JAVA; then
  printf '%s\n' "${connectors[@]}"
  exit 0
fi

# 9) scan metadata.yaml for java connectors
java_connectors=()
for c in "${connectors[@]}"; do
  metadata="airbyte-integrations/connectors/${c}/metadata.yaml"
  if [[ ! -f "$metadata" ]]; then
    echo "⚠️  metadata.yaml not found for '$c' (looking at $metadata)" >&2
    continue
  fi
  if grep -qE 'language:java' "$metadata"; then
    # echo "✅ Found java connector: '$c' (looking at $metadata)" >&2
    java_connectors+=("$c")
  fi
done

if $JAVA; then
  [ "${#java_connectors[@]}" -gt 0 ] && printf '%s\n' "${java_connectors[@]}"
  exit 0
fi

# 10) derive non-java by subtraction
non_java_connectors=()
for c in "${connectors[@]}"; do
  if ! printf '%s\n' "${java_connectors[@]}" | grep -Fxq "$c"; then
    non_java_connectors+=("$c")
  fi
done

if $NO_JAVA; then
  [ "${#non_java_connectors[@]}" -gt 0 ] && printf '%s\n' "${non_java_connectors[@]}"
  exit 0
fi

# We should never reach here
echo "⚠️  Unknown error occurred. Please check the script." >&2
exit 1

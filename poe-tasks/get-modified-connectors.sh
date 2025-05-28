#!/usr/bin/env bash

# This script is used to find all modified connector directories in the Airbyte repository.
# It compares the current branch with the default branch and filters out files that match certain ignore patterns.

set -euo pipefail

# 0) Collect arguments
DEFAULT_BRANCH="master"
JAVA=false
NO_JAVA=false
JSON=false
PREV_COMMIT=false

# parse flags
while [[ $# -gt 0 ]]; do
  case "$1" in
    --java|java)
      JAVA=true
      ;;
    --no-java|no-java)
      NO_JAVA=true
      ;;
    --json|json)
      JSON=true
      ;;
    --prev-commit|--compare-prev)
      PREV_COMMIT=true
      ;;
    *)
      echo "Unknown argument: $1" >&2;
      exit 1
      ;;
  esac
  shift
done

# 1) Fetch the latest from the default branch (using the correct remote)
if git remote get-url upstream &>/dev/null; then
  REMOTE="upstream"
else
  REMOTE="origin"
fi
git fetch --quiet "$REMOTE" "$DEFAULT_BRANCH"

# 2) set up ignore patterns
ignore_patterns=(
  '.coveragerc'
  'poe_tasks.toml'
  'README.md'
)
# join with | into a grouped regex
ignore_globs="($(IFS='|'; echo "${ignore_patterns[*]}"))$"

# 3) collect all file changes
if $PREV_COMMIT; then
  # Compare only the last commit; diff-tree is faster and more precise.
  # Intended for master, where we diff the current squashed commit against the previous squashed commit.
  committed=$(git diff-tree --no-commit-id -r --name-only HEAD)
  staged=""
  unstaged=""
  untracked=""
else
  # Default behavior
  # This is for a PR branch.
  git fetch --quiet "$REMOTE" "$DEFAULT_BRANCH"
  committed=$(git diff --name-only "${REMOTE}/${DEFAULT_BRANCH}"...HEAD)
  staged=$(git diff --cached --name-only)
  unstaged=$(git diff --name-only)
  untracked=$(git ls-files --others --exclude-standard)
fi

# 4) merge into one list
all_changes=$(printf '%s\n%s\n%s\n%s' "$committed" "$staged" "$unstaged" "$untracked")

# 5) drop ignored files
filtered=$(printf '%s\n' "$all_changes" | grep -v -E "/${ignore_globs}")

# 6) keep only connector paths
set +e # Ignore errors from grep if no matches are found
connectors_paths=$(printf '%s\n' "$filtered" | grep -E '^airbyte-integrations/connectors/(source-[^/]+|destination-[^/]+)(/|$)')
set -e

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

# 9) Define function to print either JSON or newline-delimited list.
#    JSON will be in GitHub Actions Matrix format: {"connector":[...]}
print_list() {
  if [ "$JSON" != true ]; then
    for item in "$@"; do
      echo "$item"
    done
    return
  fi

  # If JSON is requested, convert the list to JSON format.
  # This is pre-formatted to send to a GitHub Actions Matrix
  # with 'connector' as the matrix key.
  # JSON mode: emit {"connector": […]}
  if [ $# -eq 0 ]; then
    # If the list is empty, send one item as empty string.
    # This allows the matrix to run once as a no-op, and be marked as complete for purposes
    # of required checks.
    echo '{"connector": [""]}'
  else
    # If the list is not empty, convert it to JSON format.
    # This is pre-formatted to send to a GitHub Actions Matrix
    # with 'connector' as the matrix key.
    printf '%s\n' "$@" \
      | jq -R . \
      | jq -cs '{connector: .}'
  fi
}

# Allow empty arrays without 'unbound variable' error from here on out.
set +u

# 10) Print all if no filters applied

if ! $JAVA && ! $NO_JAVA; then
  print_list "${connectors[@]}"
  exit 0
fi

# 11) scan metadata.yaml to identify java connectors
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
  set +u  # Allow empty array without 'unbound variable' error
  print_list "${java_connectors[@]}"
  exit 0
fi

# 12) derive non-java by subtraction
non_java_connectors=()
for c in "${connectors[@]}"; do
  if ! printf '%s\n' "${java_connectors[@]}" | grep -Fxq "$c"; then
    non_java_connectors+=("$c")
  fi
done

if $NO_JAVA; then
  print_list "${non_java_connectors[@]}"
  exit 0
fi

# We should never reach here
echo "⚠️  Unknown error occurred. Please check the script." >&2
exit 1

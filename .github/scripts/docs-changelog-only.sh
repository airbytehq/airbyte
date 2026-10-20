#!/usr/bin/env bash
set -euo pipefail

# Checks whether the only docs changes between two commits are edits to the
# "## Changelog" section of connector docs pages (docs/integrations/**/*.md).
#
# Connector PRs add a changelog row to the connector's docs page, which would
# otherwise trigger a full Vercel preview of the docs site for a one-line edit.
#
# Exits 0 if all docs changes are changelog-only, and 1 otherwise.
#
# Usage:
#   .github/scripts/docs-changelog-only.sh <base-ref> [<head-ref>]

BASE_REF="$1"
HEAD_REF="${2:-HEAD}"

# Prints the line number of the changelog heading in a file at a given ref, or nothing.
changelog_heading_line() {
  local file="$1" ref="$2"
  git show "${ref}:${file}" 2>/dev/null | grep -n -i -m1 '^## changelog' | cut -d: -f1 || true
}

changed_files=$(git diff --no-renames --name-only "$BASE_REF" "$HEAD_REF" -- docs docusaurus .markdownlint.jsonc)
if [ -z "$changed_files" ]; then
  echo "No docs changes found."
  exit 1
fi

while read -r file; do
  case "$file" in
    docs/integrations/*.md) ;;
    *)
      echo "❌ Not a connector docs page: $file"
      exit 1
      ;;
  esac

  old_heading=$(changelog_heading_line "$file" "$BASE_REF")
  new_heading=$(changelog_heading_line "$file" "$HEAD_REF")
  if [ -z "$old_heading" ] || [ -z "$new_heading" ]; then
    echo "❌ No changelog section on both sides: $file"
    exit 1
  fi

  # Every hunk must start below the changelog heading, on both the old and new side.
  # Hunk headers look like '@@ -start[,count] +start[,count] @@'; a count of 0 means
  # that side has no lines in the hunk, so its start line doesn't matter.
  if ! git diff --no-renames -U0 "$BASE_REF" "$HEAD_REF" -- "$file" | awk \
    -v old_heading="$old_heading" -v new_heading="$new_heading" '
      /^@@ / {
        split(substr($2, 2), old, ",")
        split(substr($3, 2), new, ",")
        old_count = (old[2] == "") ? 1 : old[2]
        new_count = (new[2] == "") ? 1 : new[2]
        if ((old_count > 0 && old[1] <= old_heading) || (new_count > 0 && new[1] <= new_heading)) {
          bad = 1
        }
      }
      END { exit bad }
    '; then
    echo "❌ Changes outside the changelog section: $file"
    exit 1
  fi

  echo "✅ Changelog-only: $file"
done <<< "$changed_files"

echo "✅ All docs changes are changelog-only."

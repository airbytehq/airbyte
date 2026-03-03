#!/usr/bin/env bash

set -euo pipefail

# Adds a new changelog entry for the given connector.
# Usage: tools/bin/bulk-cdk/auto-upgrade/populate-connector-changelog.sh <connector> <new_connector_version> <pr_number> <changelog_text>
# E.g.: tools/bin/bulk-cdk/auto-upgrade/populate-connector-changelog.sh destination-dev-null 1.2.3 1234 'upgrade foo'

connector_id="$1"
new_version="$2"
pr_number="$3"
changelog_text="$4"

# Convert connector name to docs path:
# destination-dev-null -> docs/integrations/destinations/dev-null.md
# source-postgres -> docs/integrations/sources/postgres.md
connector_type=$(echo "${connector_id}" | cut -d'-' -f1)
connector_name=$(echo "${connector_id}" | cut -d'-' -f2-)
docs_file="docs/integrations/${connector_type}s/${connector_name}.md"

if ! test -f "$docs_file"; then
  echo "Docs file not found at $docs_file. This connector is probably doing something weird." >&2
  exit 1
fi

# YYYY-MM-DD format
today=$(date +%Y-%m-%d)

new_entry="| ${new_version} | ${today} | [${pr_number}](https://github.com/airbytehq/airbyte/pull/${pr_number}) | ${changelog_text} |"

# Find the changelog table and insert the new entry after the header row
# The changelog table starts with a header row (`| Version | Date | Pull Request | Subject |`),
# followed by a separator line.
# We want to insert the new entry after the separator line.
# The awk script is doing exactly that:
# When it sees a line matching the changelog header row, awk prints that line and sets the `header` flag.
# If the `header` flag is set and awk sees the separator line, awk prints the separator followed by the new changelog entry.
# Otherwise, awk just prints the line unchanged.
awk -v entry="$new_entry" '
  /^\| Version *\| Date *\| Pull Request *\| Subject *\|$/ { print; header=1; next }
  header && /^\|:?-+\|:?-+\|:?-+\|:?-+\|$/ { print; print entry; header=0; next }
  { print }
' "$docs_file" > "${docs_file}.tmp"

if cmp -s "$docs_file" "${docs_file}.tmp"; then
  echo "Error: awk command made no edits to $docs_file. Changelog table may not exist or has unexpected format." >&2
  exit 1
fi

mv "${docs_file}.tmp" "$docs_file"

echo "Added changelog entry to $docs_file"

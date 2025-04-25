#!/bin/bash

# Script to update the changelog in a connector's markdown documentation.
#
# Usage: ./update_changelog.sh <pr_number> <connector_type>-<connector_name> "<message>"
#   pr_number: The GitHub Pull Request number (e.g., 12345)
#   connector_type-connector_name: The type (source or destination) and name of the connector (e.g., source-postgres, destination-bigquery)
#   message: The description for the changelog entry (enclose in quotes)

# --- Configuration ---
DOCS_BASE_DIR="docs/integrations"
SOURCES_DIR="${DOCS_BASE_DIR}/sources" # Directory name remains plural
DESTINATIONS_DIR="${DOCS_BASE_DIR}/destinations" # Directory name remains plural
GITHUB_REPO_URL="https://github.com/airbytehq/airbyte"
CHANGELOG_HEADER="| Version | Date | Pull Request | Subject |"
# Updated Regex pattern for the separator line (using --* instead of -+)
# Matches lines like |---|---|---|---| or | :--- | -------- | ---: | :-----: | etc.
CHANGELOG_SEPARATOR_PATTERN='^[[:space:]]*\|[[:space:]]*:?--*:?[[:space:]]*\|[[:space:]]*:?--*:?[[:space:]]*\|[[:space:]]*:?--*:?[[:space:]]*\|[[:space:]]*:?--*:?[[:space:]]*\|[[:space:]]*$'


# --- Main Function ---
changelog_update() {
    # --- Argument Validation ---
    if [ "$#" -ne 3 ]; then
        echo "Usage (within script): changelog_update <pr_number> <connector_type>-<connector_name> \"<message>\""
        echo "Example: changelog_update 12345 source-postgres \"Fix data type mismatch\""
        # Exit the script if arguments are incorrect
        exit 1
    fi

    local pr_number="$1" # Use local to keep variables scoped to the function
    local full_connector_name="$2" # e.g., source-postgres
    local message="$3"
    local connector_type=""
    local connector_name=""
    local target_dir=""
    local filepath=""
    local separator_line_num=""
    local data_line_num=""
    local latest_version_line=""
    local latest_version=""
    local major=""
    local minor=""
    local patch=""
    local new_patch=""
    local new_version=""
    local today_date=""
    local pr_link=""
    local new_row=""


    # Validate PR number is a number
    if ! [[ "$pr_number" =~ ^[0-9]+$ ]]; then
        echo "Error: pr_number must be an integer."
        exit 1 # Exit script on error
    fi

    # --- Parse Connector Type and Name & Find File ---
    # Check for singular prefixes 'source-' and 'destination-'
    if [[ "$full_connector_name" == source-* ]]; then
        connector_type="source" # Use singular type for consistency
        # Remove the 'source-' prefix using parameter expansion
        connector_name="${full_connector_name#source-}"
        target_dir="${SOURCES_DIR}" # Use plural directory name
        filepath="${target_dir}/${connector_name}.md"
    elif [[ "$full_connector_name" == destination-* ]]; then
        connector_type="destination" # Use singular type for consistency
        # Remove the 'destination-' prefix
        connector_name="${full_connector_name#destination-}"
        target_dir="${DESTINATIONS_DIR}" # Use plural directory name
        filepath="${target_dir}/${connector_name}.md"
    else
        # Updated error message to reflect singular prefixes
        echo "Error: Invalid connector name format. Expected 'source-<name>' or 'destination-<name>', but got '${full_connector_name}'."
        exit 1
    fi

    # Check if the actual connector name part is empty after stripping prefix
    if [ -z "$connector_name" ]; then
        echo "Error: Connector name part is empty in '${full_connector_name}'. Expected 'source-<name>' or 'destination-<name>'."
        exit 1
    fi

    # Check if the file exists
    if [ ! -f "$filepath" ]; then
        # Updated error message slightly
        echo "Error: Could not find documentation file for connector '${connector_name}' (type: ${connector_type}) at expected path: ${filepath}"
        exit 1
    fi

    echo "Found connector file: ${filepath}"

    # --- Locate Changelog Separator Line Number using grep ---
    # Use grep -n -E to find the line number of the separator using extended regex
    # head -n 1 ensures we only get the first match if there are multiple
    echo "DEBUG: Searching for pattern '${CHANGELOG_SEPARATOR_PATTERN}' in file '${filepath}'" # Debugging line
    separator_line_num=$(grep -n -E "${CHANGELOG_SEPARATOR_PATTERN}" "$filepath" | head -n 1 | cut -d: -f1)

    if [ -z "$separator_line_num" ]; then
        echo "Error: Could not find the changelog separator pattern matching '${CHANGELOG_SEPARATOR_PATTERN}' in ${filepath}"
        # Add more debug info: show lines around where the changelog might be
        echo "DEBUG: Checking lines around the expected changelog section..."
        grep -C 5 -i "changelog" "$filepath" || echo "DEBUG: 'changelog' keyword not found."
        exit 1 # Exit script on error
    fi
    echo "DEBUG: Found separator on line number: ${separator_line_num}" # Debugging line

    # Calculate the line number for the first data row (immediately after separator)
    data_line_num=$((separator_line_num + 1))

    # --- Extract Latest Version Line using awk ---
    # Use awk to print the specific line number calculated above
    latest_version_line=$(awk -v line_num="$data_line_num" 'NR == line_num { print }' "$filepath")
    echo "DEBUG: Line content at ${data_line_num}: ${latest_version_line}" # Debugging line

    if [ -z "$latest_version_line" ]; then
        # This might happen if the separator is the very last line
        echo "Error: Found separator on line ${separator_line_num}, but could not read data from the next line (${data_line_num}) in ${filepath}"
        exit 1 # Exit script on error
    fi

    # Extract the version string from the first column (field 2 because of leading '|')
    # Use awk again for field splitting, removing leading/trailing whitespace
    latest_version=$(echo "$latest_version_line" | awk -F '|' '{gsub(/^[[:space:]]+|[[:space:]]+$/, "", $2); print $2}')

    if [ -z "$latest_version" ]; then
        echo "Error: Could not extract latest version from line ${data_line_num}: '${latest_version_line}'"
        exit 1 # Exit script on error
    fi

    echo "Latest version found: ${latest_version}"

    # --- Increment Version (Patch) ---
    # Validate basic SemVer format (X.Y.Z)
    if ! [[ "$latest_version" =~ ^[0-9]+\.[0-9]+\.[0-9]+$ ]]; then
        echo "Error: Extracted version '${latest_version}' does not look like a valid SemVer (X.Y.Z)."
        exit 1 # Exit script on error
    fi

    # Split version and increment patch number
    major=$(echo "$latest_version" | cut -d. -f1)
    minor=$(echo "$latest_version" | cut -d. -f2)
    patch=$(echo "$latest_version" | cut -d. -f3)

    new_patch=$((patch + 1))
    new_version="${major}.${minor}.${new_patch}"

    echo "New version: ${new_version}"

    # --- Prepare New Changelog Row ---
    today_date=$(date '+%Y-%m-%d')
    pr_link="[${pr_number}](${GITHUB_REPO_URL}/pull/${pr_number})"
    # Ensure message doesn't contain pipes, otherwise it breaks the table
    if [[ "$message" == *"|"* ]]; then
        echo "Warning: Message contains '|' characters. Replacing with '-' to avoid breaking table format."
        message=$(echo "$message" | tr '|' '-')
    fi

    new_row="| ${new_version} | ${today_date} | ${pr_link} | ${message} |"

    echo "New row to insert:"
    echo "$new_row"

    # --- Insert New Row into File ---
    # Use sed to find the separator line *number* and append the new row after it.
    # The -i option without an extension modifies the file in place.
    # NOTE: The new_row variable needs to be indented correctly for the sed 'a\' command.
    # We add the 10 spaces manually here.
    sed -i "${separator_line_num}a\\
${new_row}
" "$filepath"

    # Check if sed command was successful
    if [ $? -ne 0 ]; then
        echo "Error: sed command failed to insert the new row."
        # Note: No backup file to restore from.
        exit 1 # Exit script on error
    fi

    echo "Successfully updated changelog in ${filepath}"
    # Removed message about backup file

    # Function implicitly returns 0 on success if no exit code is specified
}

# Ensure the branch has the most recent updates from the master branch
git fetch origin master

# Get the list of files *modified* (status 'M') on the current branch
# since it diverged from the master branch (at the merge-base).
# We compare HEAD against the merge_base commit.
# --diff-filter=M ensures we only list files that were modified,
# excluding added (A), deleted (D), renamed (R), etc.
modified_files=$(git diff --name-only --diff-filter=M $merge_base HEAD)
echo "Modified files since merge base: $modified_files"
# Check if any files were modified
if [ -z "$modified_files" ]; then
  echo "No files were modified on the current branch compared to its merge-base with origin/master."
  connector_folders=""
else
  # Extract unique connector folder names from the list of modified files
  connector_folders=$(echo "$modified_files" | \
  grep -oP 'airbyte-integrations/connectors/\K[^/]+' | \
  sort | \
  uniq)
fi

# Process the list to get the unique connector folder names
connector_folders=$(echo "$modified_files" | \
grep -oP 'airbyte-integrations/connectors/\K[^/]+' | \
sort | \
uniq)

git pull

# Read each line from the connector_folders variable
echo "$connector_folders" | while read -r folder; do
  CONNECTOR_NAME=$(echo "$folder" | cut -d'-' -f2-)
  PR_NUM=$(gh pr list --state open --head "$1" --json number --jq '.[0].number')
  echo "The PR number is: $PR_NUM"
  changelog_update "$PR_NUM" "$folder" "Update CDK version"
  git add .
  git commit -m "Update changelog for $folder"
  git push
done
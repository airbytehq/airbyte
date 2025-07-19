#!/bin/bash

# --- Configuration ---
# Base directory for connector documentation
DOCS_BASE_DIR="docs/integrations"
# Specific directories for sources and destinations
SOURCES_DIR="${DOCS_BASE_DIR}/sources"
DESTINATIONS_DIR="${DOCS_BASE_DIR}/destinations"
# GitHub repository URL for linking Pull Requests
GITHUB_REPO_URL="https://github.com/airbytehq/airbyte"
# Expected header line in the changelog markdown table
CHANGELOG_HEADER="| Version | Date | Pull Request | Subject |"
# Regex pattern to identify the markdown table separator line (flexible for different alignments)
# Matches lines like |---|---|---|---| or | :--- | -------- | ---: | :-----: | etc.
CHANGELOG_SEPARATOR_PATTERN='^[[:space:]]*\|[[:space:]]*:?--*:?[[:space:]]*\|[[:space:]]*:?--*:?[[:space:]]*\|[[:space:]]*:?--*:?[[:space:]]*\|[[:space:]]*:?--*:?[[:space:]]*\|[[:space:]]*$'

# --- Helper Functions ---

# Function to print error messages and exit
# Usage: error_exit "Your error message" [exit_code]
error_exit() {
    local message="$1"
    local exit_code="${2:-1}" # Default exit code is 1
    echo "ERROR: ${message}" >&2
    exit "$exit_code"
}

# Function to print informational messages
# Usage: log_info "Your informational message"
log_info() {
    # Redirect echo to standard error (>&2)
    echo "INFO: ${1}" >&2
}

# Function to validate script arguments (currently expecting branch name)
# Usage: validate_script_args "$@"
validate_script_args() {
    if [ "$#" -ne 1 ]; then
        error_exit "Usage: $0 <branch_name>\nExample: $0 feature/my-connector-update"
    fi
    log_info "Script started with branch name: $1"
}

# Function to resolve the connector documentation file path
# Usage: resolve_connector_file "connector_type-connector_name"
# Returns: The full path to the markdown file or exits on error
resolve_connector_file() {
    local full_connector_name="$1"
    local connector_type=""
    local connector_name=""
    local target_dir=""
    local filepath=""

    if [[ "$full_connector_name" == source-* ]]; then
        connector_type="source"
        connector_name="${full_connector_name#source-}"
        target_dir="${SOURCES_DIR}"
    elif [[ "$full_connector_name" == destination-* ]]; then
        connector_type="destination"
        connector_name="${full_connector_name#destination-}"
        target_dir="${DESTINATIONS_DIR}"
    else
        error_exit "Invalid connector name format. Expected 'source-<name>' or 'destination-<name>', but got '${full_connector_name}'."
    fi

    if [ -z "$connector_name" ]; then
        error_exit "Connector name part is empty in '${full_connector_name}'. Expected 'source-<name>' or 'destination-<name>'."
    fi

    filepath="${target_dir}/${connector_name}.md"

    if [ ! -f "$filepath" ]; then
        error_exit "Could not find documentation file for connector '${connector_name}' (type: ${connector_type}) at expected path: ${filepath}"
    fi

    log_info "Found connector file: ${filepath}"
    echo "$filepath" # Return the filepath
}

# Function to find the line number of the changelog table separator
# Usage: find_changelog_separator_line "/path/to/connector.md"
# Returns: The line number of the separator or exits on error
find_changelog_separator_line() {
    local filepath="$1"
    local separator_line_num

    log_info "Searching for changelog separator pattern in '${filepath}'"
    separator_line_num=$(grep -n -E "${CHANGELOG_SEPARATOR_PATTERN}" "$filepath" | head -n 1 | cut -d: -f1)

    if [ -z "$separator_line_num" ]; then
        # Add more debug info if separator not found
        echo "DEBUG: Checking lines around the expected changelog section in ${filepath}..." >&2
        grep -C 5 -i "changelog" "$filepath" || echo "DEBUG: 'changelog' keyword not found." >&2
        error_exit "Could not find the changelog separator pattern matching '${CHANGELOG_SEPARATOR_PATTERN}' in ${filepath}"
    fi

    log_info "Found separator on line number: ${separator_line_num}"
    echo "$separator_line_num" # Return the line number
}

# Function to extract the latest version from the changelog
# Usage: get_latest_version "/path/to/connector.md" <data_line_number>
# Returns: The latest version string (e.g., "1.2.3") or exits on error
get_latest_version() {
    local filepath="$1"
    local data_line_num="$2"
    local latest_version_line=""
    local latest_version=""

    latest_version_line=$(awk -v line_num="$data_line_num" 'NR == line_num { print }' "$filepath")
    log_info "DEBUG: Line content at ${data_line_num}: ${latest_version_line}"

    if [ -z "$latest_version_line" ]; then
        error_exit "Found separator, but could not read data from the next line (${data_line_num}) in ${filepath}"
    fi

    # Extract version from the first column (field 2 because of leading '|')
    latest_version=$(echo "$latest_version_line" | awk -F '|' '{gsub(/^[[:space:]]+|[[:space:]]+$/, "", $2); print $2}')

    if [ -z "$latest_version" ]; then
        error_exit "Could not extract latest version from line ${data_line_num}: '${latest_version_line}'"
    fi

    # Validate basic SemVer format (X.Y.Z)
    if ! [[ "$latest_version" =~ ^[0-9]+\.[0-9]+\.[0-9]+$ ]]; then
        error_exit "Extracted version '${latest_version}' does not look like a valid SemVer (X.Y.Z)."
    fi

    log_info "Latest version found: ${latest_version}"
    echo "$latest_version" # Return the version string
}

# Function to increment the patch version of a SemVer string
# Usage: increment_version "1.2.3"
# Returns: The incremented version string (e.g., "1.2.4")
increment_version() {
    local current_version="$1"
    local major minor patch new_patch new_version

    major=$(echo "$current_version" | cut -d. -f1)
    minor=$(echo "$current_version" | cut -d. -f2)
    patch=$(echo "$current_version" | cut -d. -f3)

    new_patch=$((patch + 1))
    new_version="${major}.${minor}.${new_patch}"

    log_info "Incremented version: ${new_version}"
    echo "$new_version" # Return the new version string
}

# Function to prepare the new markdown row for the changelog
# Usage: prepare_new_changelog_row "1.2.4" 12345 "Update description"
# Returns: The formatted markdown table row string
prepare_new_changelog_row() {
    local new_version="$1"
    local pr_number="$2"
    local message="$3"
    local today_date pr_link new_row

    today_date=$(date '+%Y-%m-%d')
    pr_link="[${pr_number}](${GITHUB_REPO_URL}/pull/${pr_number})"

    # Sanitize message to avoid breaking the table
    if [[ "$message" == *"|"* ]]; then
        log_info "Warning: Message contains '|' characters. Replacing with '-'."
        message=$(echo "$message" | tr '|' '-')
    fi

    new_row="| ${new_version} | ${today_date} | ${pr_link} | ${message} |"
    log_info "Prepared new row: ${new_row}"
    echo "$new_row" # Return the new row string
}

# Function to insert the new row into the changelog file using awk
# Usage: insert_changelog_row "/path/to/connector.md" <separator_line_num> "new_markdown_row"
insert_changelog_row() {
    local filepath="$1"
    local separator_line_num="$2"
    local new_row="$3"
    local temp_file

    # Create a temporary file securely
    temp_file=$(mktemp) || error_exit "Could not create temporary file."
    # Ensure temp file is cleaned up on script exit or error
    trap 'rm -f "$temp_file"' EXIT TERM INT HUP

    log_info "Attempting to insert new row after line ${separator_line_num} in ${filepath} using awk..." >&2

    # Use awk to print existing lines and insert the new row after separator_line_num
    if ! awk -v line_num="$separator_line_num" -v new_line="$new_row" '
        1; # Print the current line (shorthand for {print $0})
        NR == line_num { print new_line } # After printing the target line (NR), print the new line
        ' "$filepath" > "$temp_file"; then
        # No need to rm temp_file here, trap will handle it
        error_exit "awk command failed while processing ${filepath}"
    fi

    # Check if awk actually produced output (basic sanity check)
    if [ ! -s "$temp_file" ]; then
         # No need to rm temp_file here, trap will handle it
        error_exit "Temporary file is empty after awk processing. Input file ${filepath} might be empty or awk failed silently."
    fi

    # Replace the original file with the modified temporary file
    if ! mv "$temp_file" "$filepath"; then
        # Temp file might still exist if mv fails, but trap should get it on exit
        error_exit "Failed to move temporary file to overwrite ${filepath}"
    fi

    # Disable the trap explicitly on successful completion of this function's critical section
    # to prevent accidental removal if the temp file was already moved.
    trap - EXIT TERM INT HUP

    log_info "Successfully inserted new row into ${filepath}" >&2
}

# --- Git Helper Functions ---

# Function to fetch updates from the master branch
# Usage: fetch_updates
fetch_updates() {
    log_info "Fetching updates from origin/master..."
    if ! git fetch origin master; then
        error_exit "Failed to fetch from origin master."
    fi
}

# Function to find the merge base between HEAD and origin/master
# Usage: find_merge_base
# Returns: The merge base commit hash or exits on error
find_merge_base() {
    local merge_base
    log_info "Finding merge base between HEAD and origin/master..."
    merge_base=$(git merge-base HEAD origin/master)

    if [ -z "$merge_base" ]; then
      error_exit "Could not find a common ancestor between HEAD and origin/master."
    fi

    log_info "Merge base commit: $merge_base"
    echo "$merge_base" # Return merge base commit hash
}

# Function to get the PR number associated with a given branch
# Usage: get_pr_number "feature/branch-name"
# Returns: The PR number or exits if not found or 'gh' fails
get_pr_number() {
    local branch_name="$1"
    local pr_num

    log_info "Attempting to find PR number for branch: ${branch_name}"

    # Use gh pr list to find the PR number for the specified head branch
    pr_num=$(gh pr list --state open --head "$branch_name" --json number --jq '.[0].number // empty')

    if [ -z "$pr_num" ]; then
        error_exit "Could not find an open PR number for branch '${branch_name}'. Make sure the PR exists and the branch name is correct."
    fi

    log_info "Found PR number: ${pr_num}"
    echo "$pr_num" # Return the PR number
}

# Function to stage, commit, and push changes for a specific connector
# Usage: stage_commit_push "connector-folder-name" "/path/to/connector.md"
stage_commit_push() {
    local folder_name="$1"
    local filepath="$2"
    local commit_message="Update changelog for $folder_name"

    log_info "Staging changes for ${filepath}"
    if ! git add "$filepath"; then
        error_exit "Failed to stage changes for ${filepath}"
    fi

    log_info "Committing changes with message: ${commit_message}"
    # Check if there are changes to commit before committing
    if git diff --staged --quiet; then
      log_info "No changes staged for ${folder_name}, skipping commit."
      return 0 # Not an error, just nothing to commit
    fi
    if ! git commit -m "$commit_message"; then
        error_exit "Failed to commit changes for ${folder_name}"
    fi

    log_info "Pushing changes to origin..."
    if ! git push; then
        # Consider adding retry logic or better error handling for push failures
        error_exit "Failed to push changes for ${folder_name}"
    fi
    log_info "Successfully committed and pushed changes for ${folder_name}"
}


# --- Main Changelog Update Logic for a Single Connector ---

# Function to update the changelog for a specific connector
# Usage: update_single_connector_changelog <pr_number> "connector_type-connector_name" "Update Message"
update_single_connector_changelog() {
    local pr_number="$1"
    local full_connector_name="$2"
    local message="$3"

    # --- Add this debug line ---
    echo "DEBUG: Value received inside function pr_number=[${pr_number}]" >&2
    # --- End of added line ---

    # Validate inputs (basic checks)
    if ! [[ "$pr_number" =~ ^[0-9]+$ ]]; then
        error_exit "Invalid PR number '${pr_number}' passed to update_single_connector_changelog."
    fi
    if [ -z "$full_connector_name" ] || [ -z "$message" ]; then
        error_exit "Connector name and message must be provided to update_single_connector_changelog."
    fi

    log_info "--- Starting changelog update for ${full_connector_name} ---"

    local filepath separator_line_num data_line_num latest_version new_version new_row

    filepath=$(resolve_connector_file "$full_connector_name")
    separator_line_num=$(find_changelog_separator_line "$filepath")
    data_line_num=$((separator_line_num + 1))
    latest_version=$(get_latest_version "$filepath" "$data_line_num")
    new_version=$(increment_version "$latest_version")
    new_row=$(prepare_new_changelog_row "$new_version" "$pr_number" "$message")
    insert_changelog_row "$filepath" "$separator_line_num" "$new_row"

    log_info "--- Completed changelog update for ${full_connector_name} ---"
    echo "$filepath" # Return the path of the modified file for git operations
}


# --- Main Execution ---
main() {
    # Enable stricter error handling
    # set -e exits immediately if a command exits with a non-zero status.
    # set -o pipefail causes a pipeline to return the exit status of the last command
    # that exited with a non-zero status, or zero if no command exited with a non-zero status.
    set -eo pipefail

    local branch_name="$1" # Expect branch name as the first argument
    validate_script_args "$@" # Validate we got the branch name

    fetch_updates
    local merge_base
    merge_base=$(find_merge_base)

    # Pull potentially new changes
    log_info "Pulling latest changes..."
    if ! git pull; then
       log_info "Warning: git pull failed, continuing with fetched state."
    fi

    local modified_connectors pr_num changelog_message updated_filepath

    if [ -z "$MODIFIED_CONNECTORS" ]; then
        log_info "No modified connectors found requiring changelog updates. Exiting."
        exit 0
    fi

    pr_num=$(get_pr_number "$branch_name")

    # Define the standard message here, could be made a script argument later
    changelog_message="Update CDK version"

    # Process each modified connector
    echo "$MODIFIED_CONNECTORS" | while IFS= read -r connector_folder; do
        # Skip empty lines just in case
        [ -z "$connector_folder" ] && continue

        log_info "Processing connector: ${connector_folder}"
        # Call the main update logic for this connector
        updated_filepath=$(update_single_connector_changelog "$pr_num" "$connector_folder" "$changelog_message")
        # Stage, commit, and push the changes for this connector's changelog
        stage_commit_push "$connector_folder" "$updated_filepath"
    done

    log_info "Script finished successfully."
}

# Execute the main function, passing all script arguments
main "$@"

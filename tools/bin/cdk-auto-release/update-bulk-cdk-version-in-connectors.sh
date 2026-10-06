#!/bin/bash

# Ensure the local repository knows about the latest state of origin/master
# This brings the commit history from the remote 'origin' for the 'master' branch
# It doesn't change your local working files or your current branch
git fetch origin master

# Find the common ancestor commit between the current branch (HEAD) and origin/master
# This identifies the point where your current branch diverged from master
merge_base=$(git merge-base HEAD origin/master)
echo "Merge base commit: $merge_base"
# Check if merge_base could be found (e.g., if branches are unrelated)
if [ -z "$merge_base" ]; then
  echo "Error: Could not find a common ancestor between HEAD and origin/master."
  exit 1
fi

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

echo "Modified connector folders (files modified on this branch only): $connector_folders"
echo "modified_connectors=$connector_folders" >> $GITHUB_OUTPUT

MODIFIED_LIST_JSON=$(echo "$connector_folders" | tr ',' '\n' | jq -R . | jq -c -s .)

echo "Modified connector folders: $MODIFIED_LIST_JSON"
echo "modified_connectors_json=$MODIFIED_LIST_JSON" >> $GITHUB_OUTPUT
# Update all modified connectors to the CDK version passed into the script.
echo "$connector_folders" | while read -r folder; do
  gradle_file="airbyte-integrations/connectors/$folder/build.gradle"
  if [ -f "$gradle_file" ]; then
    cp "$gradle_file" "$gradle_file.bak"
    sed -i "s/cdk = '.*'/cdk = '$1'/" "$gradle_file"
    sed -i "/useLocalCdk/d" "$gradle_file"

    if cmp -s "$gradle_file" "${gradle_file}.bak"; then
        # Files are identical, sed made no effective change for this command
        echo "Warning: sed command ran successfully but did not modify '$gradle_file'. Pattern 'cdk = ...' might not have been found."

        rm -f "${gradle_file}.bak" # Clean up backup
        exit 1 # Uncomment if no change should cause failure
    else
        rm -f "${gradle_file}.bak" # Clean up backup
    fi
  fi
done

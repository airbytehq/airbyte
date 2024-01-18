#!/bin/bash

# Install github cli: brew install gh

# Check if an argument was provided
if [ -z "$1" ]; then
    echo "Please provide a folder name."
    exit 1
fi

FOLDER_NAME="$1"
METADATA_FILE="$FOLDER_NAME/metadata.yaml"
SNAKE_CASED_FOLDER_NAME=$(echo "$FOLDER_NAME" | sed 's/-/_/g')
DOC_FOLDER_NAME=$(echo "$FOLDER_NAME" | sed 's/source-//')
DOC_FILE="../../docs/integrations/sources/${DOC_FOLDER_NAME}.md"
BRANCH_NAME="flash1293/airbyte-lib-convert-${FOLDER_NAME}"

git checkout origin/master
git checkout -b "$BRANCH_NAME"

# Step 1: Add entry_points to setup.py
SETUP_FILE="$FOLDER_NAME/setup.py"
if [ -f "$SETUP_FILE" ]; then
    sed -i '' "/setup(/a \\
    entry_points={\\
        \"console_scripts\": [\\
            \"${FOLDER_NAME}=${SNAKE_CASED_FOLDER_NAME}.run:run\",\\
        ],\\
    }," "$SETUP_FILE"
else
    echo "setup.py not found in $FOLDER_NAME"
    exit 1
fi

# Step 2: Create run.py and copy contents from main.py
mkdir -p "$FOLDER_NAME/$SNAKE_CASED_FOLDER_NAME"
MAIN_PY="$FOLDER_NAME/main.py"
RUN_PY="$FOLDER_NAME/$SNAKE_CASED_FOLDER_NAME/run.py"
if [ -f "$MAIN_PY" ]; then
    cp "$MAIN_PY" "$RUN_PY"
    sed -i '' 's/if __name__ == "__main__":/def run():/' "$RUN_PY"
else
    echo "main.py not found in $FOLDER_NAME"
    exit 1
fi

# Step 3: Modify main.py
echo -e "#\n# Copyright (c) 2023 Airbyte, Inc., all rights reserved.\n#\n\nfrom ${SNAKE_CASED_FOLDER_NAME}.run import run\n\nif __name__ == \"__main__\":\n    run()" > "$MAIN_PY"

# Function to update dockerImageTag
update_docker_image_tag() {
    if [ -f "$METADATA_FILE" ]; then
        # Extract the current dockerImageTag version
        CURRENT_VERSION=$(awk -F ': ' '/dockerImageTag/ {print $2}' "$METADATA_FILE" | tr -d '"')

        # Break the version into array (major, minor, patch)
        IFS='.' read -r -a VERSION_PARTS <<< "$CURRENT_VERSION"

        # Increment the patch version
        PATCH_VERSION=$((VERSION_PARTS[2] + 1))

        # Construct the new version
        NEW_VERSION="${VERSION_PARTS[0]}.${VERSION_PARTS[1]}.$PATCH_VERSION"

        # Use sed to replace the old version with the new version in metadata.yaml
        sed -i '' "s/dockerImageTag: [0-9]*\.[0-9]*\.[0-9]*/dockerImageTag: $NEW_VERSION/" "$METADATA_FILE"

        # If there is a Dockerfile in the directory, also udpate the version for the LABEL io.airbyte.version="x.y.z"
        DOCKER_FILE="$FOLDER_NAME/Dockerfile"
        if [ -f "$DOCKER_FILE" ]; then
            sed -i '' "s/LABEL io.airbyte.version=\"[0-9]*\.[0-9]*\.[0-9]*\"/LABEL io.airbyte.version=\"$NEW_VERSION\"/" "$DOCKER_FILE"
        fi

        # Return the new version
        echo "$NEW_VERSION"
    else
        echo "metadata.yaml not found in $FOLDER_NAME"
        exit 1
    fi
}

# Function to update changelog
update_changelog() {
    local version=$1
    local changelog_entry="| $version   | $(date +%Y-%m-%d) | [1234](https://github.com/airbytehq/airbyte/pull/1234) | prepare for airbyte-lib                                                        |"

    if [ -f "$DOC_FILE" ]; then
                sed -i '' -e '/|.*---.*|.*---.*|.*---.*|.*---.*/a\'$'\n'"$changelog_entry" "$DOC_FILE"

    else
        echo "Documentation file not found: $DOC_FILE"
        exit 1
    fi
}

# Main script execution
NEW_VERSION=$(update_docker_image_tag)
update_changelog "$NEW_VERSION"


echo "Modifications completed."

airbyte-ci format fix all

handle_git_operations() {
    local folder_name="$1"
    local docs_file="$2"

t    # Add changes
    git add "$folder_name"
    git add "$docs_file"

    # Commit changes
    git commit -m "convert"

    git push --set-upstream origin "$BRANCH_NAME"
}

handle_git_operations "$FOLDER_NAME" "$DOC_FILE"

# create github pr using gh tool:
gh pr create --title "$FOLDER_NAME: Convert to airbyte-lib" --body "Make the connector ready to be consumed by airbyte-lib" --base master --head "$BRANCH_NAME"
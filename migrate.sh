#!/bin/zsh

# Define an array of connector names
connector_names=("datadog")  # Replace these with your actual connector names

for name in $connector_names; do
    echo "Checking out a new branch for $name..."
    git checkout -b christo/$name-manifest-only

    # # Step to migrate to inline schemas
    # echo "Migrating to inline schemas for $name..."
    # airbyte-ci connectors --name=source-$name migrate-to-inline_schemas

    # # Ask user if the inline schema migration was successful
    # echo "Was the inline schema migration successful for $name? (y/n):"
    # read inline_migration_success

    # if [[ "$inline_migration_success" != "y" ]] && [[ "$inline_migration_success" != "Y" ]]; then
    #     echo "Inline schema migration not successful for $name. Cleaning up and skipping to next."
    #     # Clean up the directory to prepare for next task
    #     git restore airbyte-integrations/connectors/source-$name
    #     git restore docs/integrations/sources/$name.md
    #     git clean -fd airbyte-integrations/connectors/source-$name
    #     echo "Workspace cleaned up. Checking out master for $name"
    #     git checkout master
    #     git branch -D christo/$name-manifest-only
    #     continue
    # fi

    echo "Starting manifest-only migration for connector: $name"

    # Migrate connector to manifest-only format
    echo "Migrating to manifest-only..."
    airbyte-ci connectors --name=source-$name migrate-to-manifest-only

    # Ask user if the manifest-only migration was successful
    echo "Was the manifest-only migration successful for $name? (y/n):"
    read migration_success

    if [[ "$migration_success" == "y" ]] || [[ "$migration_success" == "Y" ]]; then
        echo "Proceeding with the next steps for $name..."

        # Bump connector version
        echo "Bumping version..."
        airbyte-ci connectors --name=source-$name bump-version minor "Refactor connector to manifest-only format"

        # Format fix
        echo "Applying format fixes..."
        airbyte-ci format fix js

        # Define the PR body content using mixed quotes for safety
        pr_body='## What
Migrates source-'$name' to manifest-only format

## How
Used a script to run the airbyte-ci commands [migrate-to-manifest-only, bump-version, format fix, pull-request]

## Review Guide
1. manifest.yaml: should be at the root level of the folder, list version 4.3.0, contain an inlined spec, and all $parameters should be resolved.
2. metadata.py: should list the correct manifest-only language tag, have pypi disabled, and point to a recent version of source-declarative-manifest
3. acceptance-test-config.yml: should correctly point to manifest.yaml for the spec test
4. readme.md: Should be updated with correct references to the connector
5. Pretty much everything else should be nuked

## User Impact
None'

        # Create pull request
        branch_name="christo/$name-manifest-only"
        pr_title="Source $name: Migrate to manifest-only"
        echo "Creating pull request..."
        airbyte-ci connectors --name=source-$name pull-request -m "migrate connector to manifest-only" -b $branch_name --title "$pr_title" --body "$pr_body"

        echo "Migration process completed for $name."

        # Clean up the directory to prepare for next task
        echo "Cleaning up workspace for $name..."
        git restore airbyte-integrations/connectors/source-$name
        git restore docs/integrations/sources/$name.md
        git clean -fd airbyte-integrations/connectors/source-$name
        echo "Workspace cleaned up. Checking out master for $name"
        git checkout master
        git branch -D christo/$name-manifest-only

    elif [[ "$migration_success" == "n" ]] || [[ "$migration_success" == "N" ]]; then
        echo "Migration not successful for $name. Exiting script."
        # Clean up the directory to prepare for next task
        echo "Cleaning up workspace for $name..."
        git restore airbyte-integrations/connectors/source-$name
        git restore docs/integrations/sources/$name.md
        git clean -fd airbyte-integrations/connectors/source-$name
        echo "Workspace cleaned up. Checking out master for $name"
        git checkout master
        git branch -D christo/$name-manifest-only
        # Continue to the next iteration rather than exiting
        continue
    else
        echo "Invalid input for $name. Exiting script."
        # Continue to the next iteration rather than exiting
        continue
    fi
done

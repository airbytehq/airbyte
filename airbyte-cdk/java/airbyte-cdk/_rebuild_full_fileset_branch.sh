#!/bin/bash

# This script is used to rebuild the java-cdk-010-d2 branch from scratch.
# TODO: Delete this script once the migration is complete.

# Check with the use to confirm the action
read -p "This script will delete and recreate the java-cdk-010-d2 branch. You should merge in the latest from from master before running this. Are you sure? (y/n) " -n 1 -r

# Switch to the base branch
git checkout java-cdk-010-d
# Make sure the base branch is up-to-date
# git merge origin/master
# Delete and recreate the old branch locally
git branch -D java-cdk-010-d2
git checkout -b java-cdk-010-d2
# Run the migration script
python ./airbyte-cdk/java/airbyte-cdk/_temp_migration_script.py 
# Stage the changes and commit
git add .
git commit -m "commit the migration script result"
# Force push to the origin (this PR)
git push -uf origin java-cdk-010-d2

# git cherry-pick c125f14cdce8be61da85ebedffd3c4a576dc1fc5  # delete dead code (incorrectly annotated as override)
# git cherry-pick 89d81ec62fcfa44fff36196e2d34571b46593818  # disable GlobalStateManagerTest.testToState

#!/bin/bash

# This script is used to rebuild the java-cdk-010-d2 branch from scratch.

# Check with the use to confirm the action
read -p "This script will delete and recreate the java-cdk-010-d2 branch. Are you sure? (y/n) " -n 1 -r

# Switch to the base branch
git checkout java-cdk-010-d
# Make sure the base branch is up-to-date
git merge origin/master
# Delete and recreate the old branch locally
git branch -D java-cdk-010-d2
git checkout -b java-cdk-010-d2
# Run the migration script
python ./airbyte-cdk/java/airbyte-cdk/_temp_migration_script.py 
# Stage the changes and commit
git add .
git commit -m "commit the migration script result"
# Force push to the origin (this PR)
git push -f origin java-cdk-010-d2

#!/bin/bash

echo "Bumping version in latest release branch"

MAIN_BRANCH="master"
LATEST_RELEASE_BRANCH="latest-release"

function cleanup {
    git switch $MAIN_BRANCH
}
trap cleanup EXIT

# Fetch tags, as we probably have only a shallow clone of the repo
git fetch origin "refs/tags/*:refs/tags/*"

LATEST_TAG=$(git describe --tags --abbrev=0)
echo "Most recent tag found: $LATEST_TAG"

# In case the branch exists locally, delete it silently, since we will be recreating it and force-pushing
git branch -D $LATEST_RELEASE_BRANCH &>/dev/null   

git checkout tags/$LATEST_TAG -b $LATEST_RELEASE_BRANCH

git push -f origin $LATEST_RELEASE_BRANCH

# Switch back to master
cleanup

#!/usr/bin/env bash

set -e

. tools/lib/lib.sh

PART_TO_BUMP=$1
[[ -z "$PART_TO_BUMP" ]] && echo "Usage ./tools/bin/release_version.sh (major|minor|patch)" && exit 1

# uses .bumpversion.cfg to find files to bump
# requires no git diffs to run
# commits the bumped versions code  to your branch
pip install bumpversion
VERSION=$(bumpversion --tag-message "Version {new_version}" "$PART_TO_BUMP" | grep new_version | sed -r s,"^.*=",,)

GIT_REVISION=$(git rev-parse HEAD)
[[ -z "$GIT_REVISION" ]] && echo "Couldn't get the git revision..." && exit 1

echo "Building and publishing version $VERSION for git revision $GIT_REVISION..."
./gradlew clean composeBuild
GIT_REVISION=$GIT_REVISION docker-compose -f docker-compose.build.yaml -f docker-compose.yaml build
GIT_REVISION=$GIT_REVISION docker-compose -f docker-compose.build.yaml -f docker-compose.yaml push
echo "Completed building and publishing..."

echo "Pushing bumped version code and tags..."
git push # pushes code
git push origin "v$VERSION" # pushes tag
echo "Completed..."

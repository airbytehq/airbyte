#!/usr/bin/env bash

set -e

. tools/lib/lib.sh

BRANCH=$(git rev-parse --abbrev-ref HEAD)

if [[ "$BRANCH" == "master" ]]; then
  echo 'This script should be run from a branch!';
  exit 1;
fi

PREV_VERSION=$(grep VERSION .env | cut -d"=" -f2)

PART_TO_BUMP=$1
[[ -z "$PART_TO_BUMP" ]] && echo "Usage ./tools/bin/release_version.sh (major|minor|patch)" && exit 1

# uses .bumpversion.cfg to find files to bump
# requires no git diffs to run
# commits the bumped versions code to your branch
pip install bumpversion
bumpversion "$PART_TO_BUMP"

NEW_VERSION=$(grep VERSION .env | cut -d"=" -f2)
GIT_REVISION=$(git rev-parse HEAD)
[[ -z "$GIT_REVISION" ]] && echo "Couldn't get the git revision..." && exit 1

echo "Bumped version from ${PREV_VERSION} to ${NEW_VERSION}"
echo "Building and publishing version $NEW_VERSION for git revision $GIT_REVISION..."

SUB_BUILD=PLATFORM ./gradlew clean composeBuild
VERSION=$NEW_VERSION GIT_REVISION=$GIT_REVISION docker-compose -f docker-compose.build.yaml build
VERSION=$NEW_VERSION GIT_REVISION=$GIT_REVISION docker-compose -f docker-compose.build.yaml push
echo "Completed building and publishing..."

echo
echo "Changelog:"
PAGER=cat git log v${PREV_VERSION}..${GIT_REVISION} --oneline --decorate=no

echo
echo "Final Steps:"
echo "1. Push your changes"
echo "2. Merge your PR"
echo "3. Switch to master"
echo "4. Run ./tools/bin/tag_version.sh"
echo "5. Create a GitHub release with the changelog"

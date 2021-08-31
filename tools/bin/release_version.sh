#!/usr/bin/env bash

set -e

. tools/lib/lib.sh

if [[ -z "${CLOUDREPO_USER}" ]]; then
  echo 'CLOUDREPO_USER env var not set. Please retrieve the user email from the CloudRepo lastpass secret and run export CLOUDREPO_USER=<user_from_secret>.';
  exit 1;
fi

if [[ -z "${CLOUDREPO_PASSWORD}" ]]; then
  echo 'CLOUDREPO_PASSWORD env var not set. Please retrieve the user email from the CloudRepo lastpass secret and run export CLOUDREPO_PASSWORD=<password_from_secret>.';
  exit 1;
fi

PREV_VERSION=$(grep VERSION .env | cut -d"=" -f2)

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
SUB_BUILD=PLATFORM ./gradlew publish
VERSION=$NEW_VERSION GIT_REVISION=$GIT_REVISION docker-compose -f docker-compose.build.yaml build
VERSION=$NEW_VERSION GIT_REVISION=$GIT_REVISION docker-compose -f docker-compose.build.yaml push
echo "Completed building and publishing..."

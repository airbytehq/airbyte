#!/usr/bin/env bash
set -eu
export PREV_VERSION=$(grep -w VERSION .env | cut -d"=" -f2)
export GIT_REVISION=$(git rev-parse HEAD)

pip install bumpversion
bumpversion "$PART_TO_BUMP"

export NEW_VERSION=$(grep -w VERSION .env | cut -d"=" -f2)

echo "Bumped version from ${PREV_VERSION} to ${NEW_VERSION}"
echo ::set-output name=PREV_VERSION::${PREV_VERSION}
echo ::set-output name=NEW_VERSION::${NEW_VERSION}
echo ::set-output name=GIT_REVISION::${GIT_REVISION}

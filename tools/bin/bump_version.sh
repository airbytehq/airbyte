#!/usr/bin/env bash
set -eu

# If running in a tty (TeleTYpe AKA interactive) shell
# complain because this is supposed to be run in the sky without interactive shell
if ! test "$(tty)" == "not a tty"; then
  echo "Ahoy There! This Script is meant to run as a GH action"
  exit 1
fi

set -o xtrace
PREV_VERSION=$(grep -w VERSION .env | cut -d"=" -f2)
GIT_REVISION=$(git rev-parse HEAD)

pip install bumpversion
bumpversion "$PART_TO_BUMP"

NEW_VERSION=$(grep -w VERSION .env | cut -d"=" -f2)
export VERSION=$NEW_VERSION # for safety, since lib.sh exports a VERSION that is now outdated

set +o xtrace
echo "Bumped version from ${PREV_VERSION} to ${NEW_VERSION}"
echo ::set-output name=PREV_VERSION::${PREV_VERSION}
echo ::set-output name=NEW_VERSION::${NEW_VERSION}
echo ::set-output name=GIT_REVISION::${GIT_REVISION}

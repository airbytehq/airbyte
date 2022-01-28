#!/usr/bin/env bash

set -e

. tools/lib/lib.sh

BRANCH=$(git rev-parse --abbrev-ref HEAD)
if [[ "$BRANCH" != "master" ]]; then
  echo 'This script should be run from master after merging the changes from release_version.sh!';
  exit 1;
fi

[[ ! -z "$(git status --porcelain)" ]] && echo "Cannot tag revision if all changes aren't checked in..." && exit 1

# make sure your master branch is up to date
git pull --rebase

VERSION=$(cat .env | grep -w VERSION | cut -d= -f 2)
[[ -z "$VERSION" ]] && echo "Couldn't find version in env file..." && exit 1

TAG_NAME="v$VERSION"
git tag -a "$TAG_NAME" -m "Version $VERSION"
git push origin "$TAG_NAME"

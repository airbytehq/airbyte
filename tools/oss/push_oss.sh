#!/usr/bin/env bash

set -e

_usage="
Usage: ./tools/oss/push_oss.sh <target-branch> <force (optional)>
Example: ./tools/oss/push_oss.sh my-branch force
"

function _error() {
  echo "$@"
  echo "$_usage"
  exit 1
}

function _in_sync_with_remote() {
  # https://stackoverflow.com/a/3278427
  git remote update
  UPSTREAM='@{u}'
  echo "checking local commit history against remote: $(git rev-parse --symbolic-full-name --abbrev-ref ${UPSTREAM})"
  LOCAL=$(git rev-parse @)
  REMOTE=$(git rev-parse "$UPSTREAM")
  BASE=$(git merge-base @ "$UPSTREAM")

  if [ $LOCAL = $REMOTE ]; then
      echo "Up-to-date"
  elif [ $LOCAL = $BASE ]; then
      echo "Need to pull"
  elif [ $REMOTE = $BASE ]; then
      echo "Need to push"
  else
      echo "Diverged"
  fi
}

function _on_master() {
  # only push master to downstream repo.
  CURRENT_BRANCH=$(git rev-parse --abbrev-ref HEAD)
  if [[ "$CURRENT_BRANCH" != "master" ]]; then
    _error 'Can only push to target branch master while on master branch.';
    exit 1;
  fi
}

# attempts to push the public dir to the specified branch in the dataline _public_ repository.
# * verifies that the branch being pushed is in sync with the origin remote of the monorepo.
# * allows force push (except when pushing to master--if you need to do this, do it manually).
# * only allows pushes to master from the master branch.
function main() {
  [[ -e .root ]] || _error "Must run from root"
  TARGET_BRANCH=$1; shift || _error "Missing target branch"
  FORCE_RAW=$1;
  FORCE=false

  if [[ "$FORCE_RAW" = "force" ]]; then
    FORCE=true
  fi

  echo "target branch: ${TARGET_BRANCH}"
  echo "force: ${FORCE}"

  # if pushing to master on the oss repo, must push from master.
  if [[ "$TARGET_BRANCH" = "master" ]]; then
    _on_master
  fi

  if [[ "$TARGET_BRANCH" = "master" && "$FORCE" = true ]]; then
    _error "cannot force push to master."
  fi

  # do not push to oss repo, if local branch is not in sync with origin in monorepo.
  _in_sync_with_remote

  if [[ "$FORCE" = true ]]
  then
    git push oss `git subtree split --prefix public`:"${TARGET_BRANCH}"  --force
  else
    git subtree push --prefix=public oss "${TARGET_BRANCH}"
  fi
}

main "$@"

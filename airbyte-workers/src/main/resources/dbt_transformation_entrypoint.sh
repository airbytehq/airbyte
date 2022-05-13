#!/usr/bin/env bash
set -e

#echo "about to sleep loop in dbt_transformation_entrypoint.sh"
#while true; do sleep 86400; done

echo "PARKER: GIT_REPO env var value within dbt_transformation_entrypoint: ${GIT_REPO}"


CWD=$(pwd)

POSITIONAL=()
# Detect if some mandatory dbt flags were already passed as arguments
CONTAINS_PROFILES_DIR="false"
CONTAINS_PROJECT_DIR="false"
while [[ $# -gt 0 ]]; do
  case $1 in
    --profiles-dir=*|--profiles-dir)
      CONTAINS_PROFILES_DIR="true"
      POSITIONAL+=("$1")
      shift
      ;;
    --project-dir=*|--project-dir)
      CONTAINS_PROJECT_DIR="true"
      POSITIONAL+=("$1")
      shift
      ;;
    # set GIT_REPO and GIT_BRANCH env vars based on --git-repo and --git-branch args
    # this is just for the git clone, so don't include them in POSITIONAL
    --git-repo)
      GIT_REPO="$2"
      echo "PARKER: found git-repo arg ${GIT_REPO}"
      shift 2
      ;;
    --git-branch)
      GIT_BRANCH="$2"
      echo "PARKER: found git-branch arg ${GIT_BRANCH}"
      shift 2
      ;;
    *)
      POSITIONAL+=("$1")
      shift
      ;;
  esac
done

set -- "${POSITIONAL[@]}"





# if git_repo directory does not exist, try to clone into it
# TODO (parker) see if we can remove git clone entirely from normalization's entrypoint.sh and instead always do it here.
if [[ -d git_repo ]]; then
  echo "git_repo directory already exists, reusing it."
else
  # TODO check for git cli install, throw descriptive error if not found
  ### begin git clone

  # How many commits should be downloaded from git to view history of a branch
  GIT_HISTORY_DEPTH=5

  # Make a shallow clone of the latest git repository in the workspace folder
  if [[ -z "${GIT_BRANCH}" ]]; then
    # Checkout a particular branch from the git repository
    echo "Running: git clone --depth ${GIT_HISTORY_DEPTH} --single-branch  \$GIT_REPO git_repo"
    git clone --depth ${GIT_HISTORY_DEPTH} --single-branch  "${GIT_REPO}" git_repo
  else
    # No git branch specified, use the default branch of the git repository
    echo "Running: git clone --depth ${GIT_HISTORY_DEPTH} -b ${GIT_BRANCH} --single-branch  \$GIT_REPO git_repo"
    git clone --depth ${GIT_HISTORY_DEPTH} -b "${GIT_BRANCH}" --single-branch  "${GIT_REPO}" git_repo
  fi
  # Print few history logs to make it easier for users to verify the right code version has been checked out from git
  echo "Last 5 commits in git_repo:"
  (cd git_repo; git log --oneline -${GIT_HISTORY_DEPTH}; cd -)
  ### end git clone
fi

# change directory to be inside git_repo that was just cloned
echo "cd into git_repo"
cd git_repo

echo "Running from $(pwd)"

if [[ -f "${CWD}/bq_keyfile.json" ]]; then
  cp "${CWD}/bq_keyfile.json" /tmp/bq_keyfile.json
fi

. $CWD/sshtunneling.sh
openssh $CWD/ssh.json
trap 'closessh' EXIT


#echo "sleeping before running dbt command..."
#while true; do sleep 86400; done

# Add mandatory flags profiles-dir and project-dir when calling dbt when necessary
case "${CONTAINS_PROFILES_DIR}-${CONTAINS_PROJECT_DIR}" in
  true-true)
    echo "Running: dbt $@"
    dbt $@ --profile normalize
    ;;
  true-false)
    echo "Running: dbt $@ --project-dir=${CWD}/git_repo"
    dbt $@ "--project-dir=${CWD}/git_repo" --profile normalize
    ;;
  false-true)
    echo "Running: dbt $@ --profiles-dir=${CWD}"
    dbt $@ "--profiles-dir=${CWD}" --profile normalize
    ;;
  *)
    echo "Running: dbt $@ --profiles-dir=${CWD} --project-dir=${CWD}/git_repo"
    dbt $@ "--profiles-dir=${CWD}" "--project-dir=${CWD}/git_repo" --profile normalize
    ;;
esac

closessh

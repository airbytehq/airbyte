#!/usr/bin/env bash

parse_args() {
    if [ -z "$2" ]; then
        echo "value for parameter '$1' cannot be empty"
        exit 1
    fi
    case "$1" in
        -t)
            prtype="$2"
            ;;
        -n)
            newbranch="$2"
            ;;
        -r)
            remote="$2"
            ;;
        -b)
            contributorbranch="$2"
            ;;
        -c)
            connector="$2"
            ;;
        *)
            echo "Unknown parameter '$1'." 1>&2
            exit 1
            ;;
    esac
}

check_args() {
    if [ -z $newbranch ] || [ -z $remote ] || [ -z $contributorbranch ]; then
        echo "you must provide arguments:     -n (new branch name)     -r (remote url of contributor fork)     -b (contributor branch)"   
        exit 1
    fi

    case $prtype in
        connector)
            if [ -z $connector ]; then
                echo "you must provide arguments:     -c (connector name, e.g. source-postgres)"
                exit 1
            fi
            ;;
        *)
            echo "Not implemented script for PR type '$prtype'."
            exit 1
            ;;
    esac
}

prsetup() {
    git fetch origin master &&
    git checkout master &&
    git pull &&
    git branch -d $newbranch || git checkout -b $newbranch || git checkout $newbranch &&
    git remote remove temp-contributor-remote || echo "remote 'temp-contributor-remote' doesn't exist yet" &&
    git remote add temp-contributor-remote $remote &&
    git pull temp-contributor-remote $contributorbranch --no-edit &&
    git branch --set-upstream-to=origin/$newbranch $newbranch || echo "upstream branch '$newbranch' doesn't exist yet" &&
    git push -u origin $newbranch || git pull -X ours && git push -u origin $newbranch &&
    branchsetupsuccess="true" &&
    prtitle="$" &&
    gh pr create --title "IGNORE ME :D" --body "testing" &&
    prsetupsuccess="true"

    git remote remove temp-contributor-remote
    
}

if [[ "$@" != *"-t"* ]]; then
    echo "must provide -t argument for PR type (e.g. -t connector)"
    return
fi

while [[ "$#" -ge 1 ]]; do
    parse_args "$1" "$2"
    shift; shift
done
check_args

# stash any changes in current branch
currentbranch=$(git branch --show-current)
git_stash_msg="${RANDOM}"
git stash --include-untracked -m $git_stash_msg

branchsetupsuccess="false"
prsetupsuccess="false"
prsetup

# go back to original branch and apply stash
git checkout $currentbranch &&
git stash list | grep $git_stash_msg | git stash pop && echo "reapplied stash!"

echo ""
if [ $prsetupsuccess = "false" ]; then
    if [ $branchsetupsuccess = "true" ]; then
        echo "FAILED: on PR creation, ignore if it already exists, otherwise maybe you don't have the GitHub CLI (gh) installed/setup?"
    else
        echo "ERROR: Something failed, please check output above."
    fi
else
    echo "PR successfully created / updated + test comment made! <link>"
fi

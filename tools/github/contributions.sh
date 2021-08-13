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
            prtitle="$connector: contributor PR from $remote"
            prcomment="/test connector=connectors/$connector"
            ;;
        *)
            echo "Not implemented script for PR type '$prtype'."
            exit 1
            ;;
    esac
}

prsetup() {
    # locally pull latest master changes
    git fetch origin master &&
    git checkout master &&
    git pull &&
    # locally checkout newbranch (either for the first time or if it already exists)  
    git checkout -b $newbranch || git checkout $newbranch &&
    # generate temporary name to call the remote repo based on the url
    remotearray=($(echo $remote | tr "/" " "))
    remotename=${remotearray[${#remotearray[@]}-2]}-${remotearray[${#remotearray[@]}-1]}
    # attempt to add remote, with echo WARN if it fails as it may have already been added 
    git remote add $remotename $remote || echo "WARN: remote might already be added" &&
    # pull latest changes from contributors fork branch into your local newbranch
    git pull $remotename $contributorbranch --no-edit &&
    # this may be redundant but ensure upstream set correctly for our newbranch and then push up changes
    git branch --set-upstream-to=origin/$newbranch $newbranch || echo "WARN: upstream branch '$newbranch' doesn't exist yet" &&
    git push -u origin $newbranch &&
    branchsetupsuccess="true"

    # using GitHub cli (gh) create PR, this will fail if already exists so we echo WARN
    gh pr create --title "$prtitle" --body "Clone of contributor PR to run tests etc." || echo "WARN: PR may already exist" &&
    # add comment to the PR to run desired test
    gh pr comment $newbranch --body "$prcomment" &&
    prsetupsuccess="true"
    # try to grab URL for PR to output at end of script
    prlink=$(gh pr list -L 1000 --jq ".[] | select(.title==\"$prtitle\").url" --json title,url)

    # remove the local connection to forked repo remote
    git remote remove $remotename
    
}

main() {
    # ensure -t argument is passed in, this determines type of PR (e.g. connector)
    if [[ "$@" != *"-t"* ]]; then
        echo "must provide -t argument for PR type (e.g. -t connector)"
        exit 1
    fi

    # parse all the arguments and then check them (see functions above)
    while [[ "$#" -ge 1 ]]; do
        parse_args "$1" "$2"
        shift; shift
    done
    check_args

    # stash any changes from current branch before we run prsetup
    currentbranch=$(git branch --show-current)
    git_stash_msg="${RANDOM}"
    git stash --include-untracked -m $git_stash_msg

    branchsetupsuccess="false"
    prsetupsuccess="false"
    prsetup

    # go back to original branch and apply stash if there was one
    git checkout $currentbranch &&
    git stash list | grep $git_stash_msg | git stash pop && echo "reapplied stash!"

    echo ""
    if [ $prsetupsuccess = "false" ]; then
        if [ $branchsetupsuccess = "true" ]; then
            echo "FAILED: on PR creation, maybe you don't have the GitHub CLI (gh) installed/setup? Check output above."
        else
            echo "ERROR: Something failed, please check output above."
        fi
    else
        echo "PR successfully created / updated + test comment made! $prlink"
    fi
}

main "$@"
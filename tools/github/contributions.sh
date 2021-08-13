
parse_args() {
    if [ -z "$2" ]; then
        echo "value for parameter '$1' cannot be empty"
        exit 1
    fi
    case "$1" in
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

prsetup() {
    git fetch origin master &&
    git checkout master &&
    git pull &&
    git branch -D $newbranch || echo "branch '$newbranch' doesn't exist yet" &&
    git checkout -b $newbranch &&
    git remote remove temp-contributor-remote || echo "remote 'temp-contributor-remote' doesn't exist yet" &&
    git remote add temp-contributor-remote $remote &&
    git pull temp-contributor-remote $contributorbranch --no-edit &&
    prsetupsuccess="true"

    git remote remove temp-contributor-remote
    
}

if [[ "$#" -le 7 ]]; then
    echo "you must provide arguments:\n    -n (new branch name)\n    -r (remote url of contributor fork)\n    -b (contributor branch)\n    -c (connector name, e.g. source-postgres)"
    return
fi

while [[ "$#" -ge 1 ]]; do
    parse_args "$1" "$2"
    shift; shift
done

# stash any changes in current branch
currentbranch=$(git branch --show-current)
git_stash_msg="${RANDOM}"
git stash --include-untracked -m $git_stash_msg

prsetupsuccess="false" &&
prsetup

# go back to original branch and apply stash
git checkout $currentbranch 
git stash list | grep $git_stash_msg | git stash pop && echo "applied stash!"

echo ""
if [ $prsetupsuccess = "false" ]; then
    echo "ERROR: Something failed, please check output above."
else
    echo "PR successfully created! <link>"
fi

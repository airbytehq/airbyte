
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
git stash --include-untracked

git fetch origin master
git checkout master
git branch -D $newbranch
git checkout -b $newbranch
git pull $remote $remote/$contributorbranch

# go back to original branch and apply stash
git checkout $currentbranch
git stash apply

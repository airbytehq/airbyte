#!/usr/bin/env bash

retries=3

function pull_dockerhub_image_with_retries() {
    local image=$1
    local retries=$2

    for (( i=1; i<=$retries; i++ )); do
        docker pull $image
        # NOTE: this does not discriminate on the failure, any failure will retry
        test "$?" -eq 0 && return || echo "Docker pull failed, sleeping for 5 seconds before retrying ($i/$retries)" && sleep 5
    done
}

function main() {
    while getopts ':i:r:' OPTION; do
        case "$OPTION" in
            i)
                image="$OPTARG"
                ;;
            r)
                if [[ "$OPTARG" =~ ^(-)?[0-9]+$ ]]; then
                    retries="$OPTARG"
                else
                    echo "retries (-r) must be a number" && exit 1
                fi
                ;;
            ?)
                echo "script usage: $(basename "$0") [-i image] [-r retries]" >&2
                exit 1
                ;;
        esac
    done
    shift "$(($OPTIND -1))"

    pull_dockerhub_image_with_retries $image $retries
}

main "$@"



#!/usr/bin/env bash
this_dir=$(cd $(dirname "$0"); pwd) # this script's directory
this_script=$(basename $0)


docker image tag airbyte/destination-glide:dev activescott/destination-glide:dev

docker push activescott/destination-glide:dev


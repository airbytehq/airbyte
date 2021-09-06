#!/usr/bin/env bash

IMG_TAG="airbyte/openapi2jsonschema"

test "$#" == "0" &&  {
   echo "Please specify path to open api definition file"
   exit
}

docker images | grep "$IMG_TAG"  > /dev/null || {
   pushd $(dirname ${BASH_SOURCE[0]})
   docker build . -t $IMG_TAG
   popd
}

tmp_dir=$(mktemp -d)
cp $1 $tmp_dir || exit
tmp_file=$(basename $1)

docker run --rm \
   --name openapi2jsonschema \
   --user $(id -u):$(id -g)\
   -v $tmp_dir:/schemas \
   $IMG_TAG --stand-alone --no-all ./$tmp_file

cp -rf $tmp_dir/schemas ./

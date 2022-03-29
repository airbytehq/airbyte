#! /bin/bash

REV="${1}"

if [ X${REV} = X ]
then
	REV=dev
fi
echo $REV

docker build . -t airbyte/destination-aws-datalake:$REV

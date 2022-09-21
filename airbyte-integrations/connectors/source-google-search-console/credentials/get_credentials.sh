#!/bin/bash

docker build . -t airbyte-get-gsc-credentials
docker run --name airbyte-get-gsc-credentials -t -d airbyte-get-gsc-credentials
docker exec -it airbyte-get-gsc-credentials python get_authentication_url.py
echo "Input your code:"
read code
docker exec -it airbyte-get-gsc-credentials python get_refresh_token.py $code
docker rm airbyte-get-gsc-credentials --force

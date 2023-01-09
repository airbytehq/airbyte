#!/bin/bash

NAME="airbyte-proxy-test-container"
PORT=18000
BASIC_AUTH_USERNAME=airbyte
BASIC_AUTH_PASSWORD=password
BASIC_AUTH_UPDATED_PASSWORD=pa55w0rd
BASIC_AUTH_PROXY_TIMEOUT=120
TEST_HOST=localhost
VERSION="${VERSION:-dev}" # defaults to "dev", otherwise it is set by environment's $VERSION

echo "testing with proxy container airbyte/proxy:$VERSION"

function start_container () {
  CMD="docker run -d -p $PORT:8000 --env BASIC_AUTH_USERNAME=$1 --env BASIC_AUTH_PASSWORD=$2 --env BASIC_AUTH_PROXY_TIMEOUT=$3 --env PROXY_PASS_WEB=http://localhost --env PROXY_PASS_API=http://localhost --env CONNECTOR_BUILDER_SERVER_API=http://localhost --name $NAME airbyte/proxy:$VERSION"
  echo $CMD
  eval $CMD
  wait_for_docker;
}

function start_container_with_proxy () {
  CMD="docker run -d -p $PORT:8000 --env PROXY_PASS_WEB=$1 --env PROXY_PASS_API=$1 --name $NAME
  airbyte/proxy:$VERSION"
  echo $CMD
  eval $CMD
  wait_for_docker;
}

function stop_container () {
  echo "Stopping $NAME"
  docker kill $NAME
  docker rm $NAME
}

function wait_for_docker() {
  until [ "`docker inspect -f {{.State.Running}} $NAME`"=="true" ]; do
    sleep 1;
  done;
  sleep 1;
}

echo "Testing airbyte proxy..."

stop_container; # just in case there was a failure of a previous test run

echo "Starting $NAME"
start_container $BASIC_AUTH_USERNAME $BASIC_AUTH_PASSWORD $BASIC_AUTH_PROXY_TIMEOUT

echo "Testing access without auth"
RESPONSE=`curl "http://$TEST_HOST:$PORT" -i --silent`
if [[ $RESPONSE == *"401 Unauthorized"* ]]; then
  echo "✔️  access without auth blocked"
else
  echo "Auth not working"
  echo $RESPONSE
  exit 1
fi

echo "Testing access with auth"
RESPONSE=`curl "http://$BASIC_AUTH_USERNAME:$BASIC_AUTH_PASSWORD@$TEST_HOST:$PORT" -i --silent`
if [[ $RESPONSE != *"401 Unauthorized"* ]]; then
  echo "✔️  access with auth worked"
else
  echo "Auth not working"
  echo $RESPONSE
  exit 1
fi

stop_container;

echo "Starting $NAME with updated password"
start_container $BASIC_AUTH_USERNAME $BASIC_AUTH_UPDATED_PASSWORD $BASIC_AUTH_PROXY_TIMEOUT

echo "Testing access with orignial paassword"
RESPONSE=`curl "http://$BASIC_AUTH_USERNAME:$BASIC_AUTH_PASSWORD@$TEST_HOST:$PORT" -i --silent`
if [[ $RESPONSE == *"401 Unauthorized"* ]]; then
  echo "✔️  access with original auth blocked"
else
  echo "Auth not working"
  echo $RESPONSE
  exit 1
fi

echo "Testing access updated auth"
RESPONSE=`curl "http://$BASIC_AUTH_USERNAME:$BASIC_AUTH_UPDATED_PASSWORD@$TEST_HOST:$PORT" -i --silent`
if [[ $RESPONSE != *"401 Unauthorized"* ]]; then
  echo "✔️  access with updated auth worked"
else
  echo "Auth not working"
  echo $RESPONSE
  exit 1
fi

stop_container;

echo "Starting $NAME with no password"
start_container "" ""

echo "Testing access without auth"
RESPONSE=`curl "http://$TEST_HOST:$PORT" -i --silent`
if [[ $RESPONSE != *"401 Unauthorized"* ]]; then
  echo "✔️  access without auth allowed when configured"
else
  echo "Auth not working"
  echo $RESPONSE
  exit 1
fi

stop_container;


# TODO: We can't test external URLs without a resolver, but adding a resolver that isn't dynamic+local doesn't work with docker.

# echo "Testing that PROXY_PASS can be used to change the backend"
# start_container_with_proxy "http://www.google.com"

# RESPONSE=`curl "http://$TEST_HOST:$PORT" -i --silent`
# if [[ $RESPONSE == *"google.com"* ]]; then
#   echo "✔️  proxy backends can be changed"
# else
#   echo "Proxy update not working"
#   echo $RESPONSE
#   exit 1
# fi

# stop_container;

echo "Tests Passed ✅"
exit 0

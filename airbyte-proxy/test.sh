#!/bin/bash

NAME="airbyte-proxy-test-container"
PORT=18000
BASIC_AUTH_USERNAME=airbyte
BASIC_AUTH_PASSWORD=password
BASIC_AUTH_UPDATED_PASSWORD=pa55w0rd

function start_container () {
  docker run -d -p $PORT:8000 --env BASIC_AUTH_USERNAME=$1 --env BASIC_AUTH_PASSWORD=$2 --name $NAME airbyte/proxy:dev
  docker run --rm jwilder/dockerize -wait tcp://host.docker.internal:$PORT -timeout 30s
}

function start_container_with_proxy () {
  docker run -d -p $PORT:8000 --env PROXY_PASS_WEB=$3 --name $NAME airbyte/proxy:dev
  docker run --rm jwilder/dockerize -wait tcp://host.docker.internal:$PORT -timeout 30s
}

function stop_container () {
  echo "Stopping $NAME"
  docker stop $NAME
  docker rm $NAME
}

echo "Testing airbyte proxy..."

stop_container; # just in case there was a failure of a previous test run

echo "Starting $NAME"
start_container $BASIC_AUTH_USERNAME $BASIC_AUTH_PASSWORD

echo "Testing access without auth"
RESPONSE=`curl "http://localhost:$PORT" -i --silent`
if [[ $RESPONSE == *"401 Unauthorized"* ]]; then
  echo "✔️  access without auth blocked"
else
  echo "Auth not working"
  echo $RESPONSE
  exit 1
fi

echo "Testing access with auth"
RESPONSE=`curl "http://$BASIC_AUTH_USERNAME:$BASIC_AUTH_PASSWORD@localhost:$PORT" -i --silent`
if [[ $RESPONSE == *"200 OK"* ]]; then
  echo "✔️  access with auth worked"
else
  echo "Auth not working"
  echo $RESPONSE
  exit 1
fi

stop_container;

echo "Starting $NAME with updated password"
start_container $BASIC_AUTH_USERNAME $BASIC_AUTH_UPDATED_PASSWORD

echo "Testing access with orignial paassword"
RESPONSE=`curl "http://$BASIC_AUTH_USERNAME:$BASIC_AUTH_PASSWORD@localhost:$PORT" -i --silent`
if [[ $RESPONSE == *"401 Unauthorized"* ]]; then
  echo "✔️  access with original auth blocked"
else
  echo "Auth not working"
  echo $RESPONSE
  exit 1
fi

echo "Testing access updated auth"
RESPONSE=`curl "http://$BASIC_AUTH_USERNAME:$BASIC_AUTH_UPDATED_PASSWORD@localhost:$PORT" -i --silent`
if [[ $RESPONSE == *"200 OK"* ]]; then
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
RESPONSE=`curl "http://localhost:$PORT" -i --silent`
if [[ $RESPONSE == *"200 OK"* ]]; then
  echo "✔️  access without auth allowed when configured"
else
  echo "Auth not working"
  echo $RESPONSE
  exit 1
fi

stop_container;

echo "Testing that PROXY_PASS can be used to change the backend"
start_container_with_proxy $BASIC_AUTH_USERNAME $BASIC_AUTH_UPDATED_PASSWORD "https://www.google.com"

RESPONSE=`curl "http://localhost:$PORT" -i --silent`
if [[ $RESPONSE == *"google.com"* ]]; then
  echo "✔️  access without auth allowed when configured"
else
  echo "Proxy update not working"
  echo $RESPONSE
  exit 1
fi

stop_container;

echo "Tests Passed ✅"
exit 0

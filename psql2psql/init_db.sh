#!/bin/bash
CONTAINER_NAME=
IMG=postgres:11.6

function _delete_container_if_exists() {
  # kill if exists.
  echo "killing ${CONTAINER_NAME}"
  docker rm -f ${CONTAINER_NAME} 2> /dev/null || true
}

function _wait_until_db_is_ready() {
  RETRIES=5

  until docker exec "${CONTAINER_NAME}" /bin/sh -c "psql -h localhost -p 5432 -U postgres -d postgres -c \"select 1\"" > /dev/null 2>&1 || [ $RETRIES -eq 0 ]; do
    echo "Waiting for postgres server, $((RETRIES--)) remaining attempts..."
    sleep 1
  done
}

function _seed_db(){
  INIT_SCRIPT=$1
  INIT_SCRIPT_TARGET_NAME=initscript
  echo $INIT_SCRIPT_TARGET_NAME
  docker cp "$INIT_SCRIPT" ${CONTAINER_NAME}:/docker-entrypoint-initdb.d/"${INIT_SCRIPT_TARGET_NAME}".sql
  docker exec -u postgres "$CONTAINER_NAME" psql postgres postgres -f docker-entrypoint-initdb.d/"${INIT_SCRIPT_TARGET_NAME}".sql
}

function main(){
  CONTAINER_NAME=$1
  PORT=$2
  INIT_SCRIPT=$3
  _delete_container_if_exists
  docker run --name "${CONTAINER_NAME}" -p "${2}":5432 -d ${IMG} # run db
  _wait_until_db_is_ready

  if [ -n "$INIT_SCRIPT" ]; then
    _seed_db "$INIT_SCRIPT"
  fi
}

main "$@"


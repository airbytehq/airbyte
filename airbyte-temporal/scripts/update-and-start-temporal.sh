#!/usr/bin/env bash

DBNAME="${DBNAME:-temporal}"
VISIBILITY_DBNAME="${VISIBILITY_DBNAME:-temporal_visibility}"
DB_PORT="${DB_PORT:-3306}"

POSTGRES_SEEDS="${POSTGRES_SEEDS:-}"
POSTGRES_USER="${POSTGRES_USER:-}"
POSTGRES_PWD="${POSTGRES_PWD:-}"

SCHEMA_DIR=${TEMPORAL_HOME}/schema/postgresql/v96/temporal/versioned
VISIBILITY_SCHEMA_DIR=${TEMPORAL_HOME}/schema/postgresql/v96/visibility/versioned

SKIP_DEFAULT_NAMESPACE_CREATION="${SKIP_DEFAULT_NAMESPACE_CREATION:-false}"
DEFAULT_NAMESPACE="${DEFAULT_NAMESPACE:-default}"
DEFAULT_NAMESPACE_RETENTION=${DEFAULT_NAMESPACE_RETENTION:-1}

# See https://github.com/temporalio/temporal/blob/release/v1.13.x/docker/entrypoint.sh
init_entry_point() {
  echo "Start init"
  export BIND_ON_IP="${BIND_ON_IP:-$(hostname -i)}"

  if [[ "${BIND_ON_IP}" =~ ":" ]]; then
      # ipv6
      export TEMPORAL_CLI_ADDRESS="[${BIND_ON_IP}]:7233"
  else
      # ipv4
      export TEMPORAL_CLI_ADDRESS="${BIND_ON_IP}:7233"
  fi

  dockerize -template ./config/config_template.yaml:./config/docker.yaml
  echo "Done init"
}

wait_for_postgres() {
  until nc -z "${POSTGRES_SEEDS%%,*}" "${DB_PORT}"; do
      echo 'Waiting for PostgreSQL to startup.'
      sleep 1
  done

  echo 'PostgreSQL started.'
}

update_postgres_schema() {
  { export SQL_PASSWORD=${POSTGRES_PWD}; } 2> /dev/null

  CONTAINER_ALREADY_STARTED="CONTAINER_ALREADY_STARTED_PLACEHOLDER"
  if [ ! -e $CONTAINER_ALREADY_STARTED ]; then
      touch $CONTAINER_ALREADY_STARTED
      temporal-sql-tool --plugin postgres --ep "${POSTGRES_SEEDS}" -u "${POSTGRES_USER}" -p "${DB_PORT}" create --db "${DBNAME}"
      temporal-sql-tool --plugin postgres --ep "${POSTGRES_SEEDS}" -u "${POSTGRES_USER}" -p "${DB_PORT}" --db "${DBNAME}" setup-schema -v 0.0


      temporal-sql-tool --plugin postgres --ep "${POSTGRES_SEEDS}" -u "${POSTGRES_USER}" -p "${DB_PORT}" create --db "${VISIBILITY_DBNAME}"
      temporal-sql-tool --plugin postgres --ep "${POSTGRES_SEEDS}" -u "${POSTGRES_USER}" -p "${DB_PORT}" --db "${VISIBILITY_DBNAME}" setup-schema -v 0.0
  fi
  echo "Starting to update the temporal DB"
  temporal-sql-tool --plugin postgres --ep "${POSTGRES_SEEDS}" -u "${POSTGRES_USER}" -p "${DB_PORT}" --db "${DBNAME}" update-schema -d "${SCHEMA_DIR}"
  echo "Update the temporal DB is done"

  echo "Starting to update the temporal visibility DB"
  temporal-sql-tool --plugin postgres --ep "${POSTGRES_SEEDS}" -u "${POSTGRES_USER}" -p "${DB_PORT}" --db "${VISIBILITY_DBNAME}" update-schema -d "${VISIBILITY_SCHEMA_DIR}"
  echo "Update the temporal visibility DB is done"

}

setup_server(){
    echo "Temporal CLI address: ${TEMPORAL_CLI_ADDRESS}."

    until tctl cluster health | grep SERVING; do
        echo "Waiting for Temporal server to start..."
        sleep 1
    done
    echo "Temporal server started."

    if [ "${SKIP_DEFAULT_NAMESPACE_CREATION}" != true ]; then
        register_default_namespace
    fi

    if [ "${SKIP_ADD_CUSTOM_SEARCH_ATTRIBUTES}" != true ]; then
        add_custom_search_attributes
    fi
}
register_default_namespace() {
    echo "Registering default namespace: ${DEFAULT_NAMESPACE}."
    if ! tctl --ns "${DEFAULT_NAMESPACE}" namespace describe; then
        echo "Default namespace ${DEFAULT_NAMESPACE} not found. Creating..."
        tctl --ns "${DEFAULT_NAMESPACE}" namespace register --rd "${DEFAULT_NAMESPACE_RETENTION}" --desc "Default namespace for Temporal Server."
        echo "Default namespace ${DEFAULT_NAMESPACE} registration complete."
    else
        echo "Default namespace ${DEFAULT_NAMESPACE} already registered."
    fi
}

add_custom_search_attributes() {
      echo "Adding Custom*Field search attributes."
      # TODO: Remove CustomStringField
# @@@SNIPSTART add-custom-search-attributes-for-testing-command
      tctl --auto_confirm admin cluster add-search-attributes \
          --name CustomKeywordField --type Keyword \
          --name CustomStringField --type Text \
          --name CustomTextField --type Text \
          --name CustomIntField --type Int \
          --name CustomDatetimeField --type Datetime \
          --name CustomDoubleField --type Double \
          --name CustomBoolField --type Bool
# @@@SNIPEND
}

setup_server(){
    echo "Temporal CLI address: ${TEMPORAL_CLI_ADDRESS}."

    until tctl cluster health | grep SERVING; do
        echo "Waiting for Temporal server to start..."
        sleep 1
    done
    echo "Temporal server started."

    if [ "${SKIP_DEFAULT_NAMESPACE_CREATION}" != true ]; then
        register_default_namespace
    fi

    if [ "${SKIP_ADD_CUSTOM_SEARCH_ATTRIBUTES}" != true ]; then
        add_custom_search_attributes
    fi
}

init_entry_point
wait_for_postgres
update_postgres_schema

echo "starting temporal server"
setup_server &
./start-temporal.sh

#!/usr/bin/env bash
trap 'kill $ABID; kill $AFID; kill $SSID; kill $PGID; exit' INT
(
    cd ../../..
    echo "Starting Airbyte..."
    docker-compose down -v
    docker-compose up -d
)&
ABID=$!
(
    echo "Starting Airflow..."
    docker-compose -f docker-compose-airflow.yaml down -v
    docker-compose -f docker-compose-airflow.yaml up -d
)&
AFID=$!
(
    echo "Starting Superset..."
    docker-compose -f superset/docker-compose-superset.yaml down -v
    docker-compose -f superset/docker-compose-superset.yaml up -d
)&
SSID=$!
(
    echo "Creating PG destination (localhost:2000 postgres/password)"
    docker rm --force airbyte-destination
    docker run --rm --name airbyte-destination -e POSTGRES_PASSWORD=password -p 2000:5432 -d postgres
)&
PGID=$!
echo "Waiting for applications to start..."
wait
echo "Access Airbyte at http://localhost:8000 and set up a connection."
echo "Enter your Airbyte connection ID: "
read connection_id
# Set connection ID for DAG.
docker exec -ti airflow_webserver airflow variables set 'AIRBYTE_CONNECTION_ID' "$connection_id"
docker exec -ti airflow_webserver airflow connections add 'airbyte_example' --conn-uri 'airbyte://host.docker.internal:8000'
echo "Access Airflow at http://localhost:8085 to kick off your Airbyte sync DAG."
echo "Access Superset at http://localhost:8088 to set up your dashboards."
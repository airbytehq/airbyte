#!/usr/bin/env bash
cd ../../..
docker-compose down -v
cd resources/examples/airflow || exit
docker-compose -f docker-compose-superset.yaml down -v
docker-compose -f docker-compose.yaml down -v
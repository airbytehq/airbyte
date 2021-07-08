#!/usr/bin/env bash
cd ../../..
docker-compose down -v
cd resources/examples/airflow || exit
docker-compose -f docker-compose-superset.yaml down -v --remove-orphans
docker-compose -f docker-compose-airflow.yaml down -v --remove-orphans
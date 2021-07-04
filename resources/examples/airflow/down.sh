#!/usr/bin/env bash
cd ../../..
docker-compose down -v
cd resources/examples/airflow || exit
docker-compose down -v
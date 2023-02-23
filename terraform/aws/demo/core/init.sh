#!/usr/bin/env bash

set -ex

install_init() {
  sudo yum update -y
}

install_docker() {
  sudo yum install -y docker
  sudo service docker start
  sudo usermod -a -G docker ec2-user
}

install_docker_compose() {
  sudo wget https://github.com/docker/compose/releases/download/1.26.2/docker-compose-$(uname -s)-$(uname -m) -O /usr/local/bin/docker-compose
  sudo chmod +x /usr/local/bin/docker-compose
  docker-compose --version
}

install_airbyte() {
  mkdir airbyte && cd airbyte
  wget https://raw.githubusercontent.com/airbytehq/airbyte/master/{.env,docker-compose.yaml}
  API_URL=/api/v1/ AIRBYTE_ROLE=demo docker-compose up -d
}

install_demo_pg() {
  docker run --rm --name postgres-demo -e POSTGRES_PASSWORD=password -p 3000:5432 -d postgres
  docker exec postgres-demo psql -U postgres -c 'create database analytics;'
  docker exec postgres-demo psql -U postgres -c 'grant all privileges on database analytics to postgres;'
}

main() {
  install_init
  install_docker
  install_docker_compose
  install_airbyte
  install_demo_pg
}

main > /tmp/init.log 2>&1

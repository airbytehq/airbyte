#!/usr/bin/env bash

set -ex

install_init() {
  sudo apt-get update
  sudo apt-get install -y apt-transport-https ca-certificates curl gnupg2 software-properties-common wget
}

install_docker() {
  curl -fsSL https://download.docker.com/linux/debian/gpg | sudo apt-key add --
  sudo add-apt-repository "deb [arch=amd64] https://download.docker.com/linux/debian buster stable"
  sudo apt-get update
  sudo apt-get install -y containerd.io
  sudo apt-get install -y docker-ce docker-ce-cli || true
  sudo service docker start
}

install_docker_compose() {
  sudo wget "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -O /usr/local/bin/docker-compose
  sudo chmod +x /usr/local/bin/docker-compose
  docker-compose --version
}

install_airbyte() {
  mkdir airbyte && cd airbyte
  wget https://raw.githubusercontent.com/airbytehq/airbyte/master/{.env,docker-compose.yaml}
  API_URL=/api/v1/ docker-compose up -d
}

main() {
  install_init
  install_docker
  install_docker_compose
  install_airbyte
}

main > /tmp/init.log 2>&1

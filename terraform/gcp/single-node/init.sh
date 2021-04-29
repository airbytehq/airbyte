#!/usr/bin/env bash

set -ex

install_init() {
  sudo apt-get update -y
  sudo apt-get install -y wget
}

install_docker() {
  sudo apt-get update
  sudo apt-get install -y apt-transport-https ca-certificates curl gnupg2 software-properties-common
  curl -fsSL https://download.docker.com/linux/debian/gpg | sudo apt-key add --
  sudo add-apt-repository "deb [arch=amd64] https://download.docker.com/linux/debian buster stable"
  sudo apt-get update
  sudo apt-get install -y docker-ce docker-ce-cli containerd.io
}

install_docker_compose() {
  sudo wget https://github.com/docker/compose/releases/download/1.26.2/docker-compose-$(uname -s)-$(uname -m) -O /usr/local/bin/docker-compose
  sudo chmod +x /usr/local/bin/docker-compose
  sudo docker-compose --version
}

install_airbyte() {
  mkdir airbyte && cd airbyte
  wget https://raw.githubusercontent.com/airbytehq/airbyte/master/.env
  wget https://raw.githubusercontent.com/airbytehq/airbyte/master/docker-compose.yaml
  sudo docker-compose up -d
}

install_stackdriver_agent() {
  curl -sSO https://dl.google.com/cloudagents/install-monitoring-agent.sh
  sudo bash install-monitoring-agent.sh
}

main() {
  install_init
  install_docker
  install_docker_compose
  install_stackdriver_agent
  install_airbyte
}

main

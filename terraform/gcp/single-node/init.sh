#!/usr/bin/env bash

set -ex

install_init() {
  sudo apt-get update -y
  sudo apt-get install -y wget
}

install_docker() {
  sudo apt-get update
  sudo apt-get install -y apt-transport-https ca-certificates curl gnupg lsb-release
  curl -fsSL https://download.docker.com/linux/debian/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg
  echo "deb [arch=amd64 signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/debian $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
  sudo apt-get update
  # this reliably shows an error when launching the docker daemon but immediately succeeds afterwards
  sudo apt-get install -y docker-ce docker-ce-cli containerd.io || true
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
  sudo service stackdriver-agent start
}

main() {
  install_init
  install_docker
  install_docker_compose
  install_stackdriver_agent
  install_airbyte
}

main

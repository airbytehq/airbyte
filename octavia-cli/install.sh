#!/usr/bin/env bash
# THIS INSTALL SCRIPT IS A WORK IN PROGRESS
# It currently only works for ZSH and does not check for previous install
# It creates an octavia alias in ~/.zshrc bound to a docker run command
set -eu
VERSION=dev

check_docker_is_running() {
    if ! docker info > /dev/null 2>&1; then
    echo "This script uses docker, and it isn't running - please start docker and try again!"
    exit 1
    fi
}

pull_image() {
    docker pull airbyte/octavia-cli:${VERSION}
}

add_alias() {
    echo 'alias octavia="pwd | xargs -I {} docker run --rm -v {}:/home/octavia-project --network host -e AIRBYTE_URL="${AIRBYTE_URL}" -e AIRBYTE_WORKSPACE_ID="${AIRBYTE_WORKSPACE_ID}" airbyte/octavia-cli:'${VERSION}'"'  >> ~/.zshrc
    echo "octavia alias was added to .zshrc , please open a new terminal window or run source ~/.zshrc"
}

install () {
    check_docker_is_running
    # pull_image # uncomment this when we publish the image to our docker registry
    add_alias
}

while true; do
    read -p "This install script only works for ZSH, are you using ZSH? (Y/n):" yn
    case $yn in
        [Yy]* ) install; break;;
        [Nn]* ) exit;;
        * ) echo "Please answer yes or no.";;
    esac
done
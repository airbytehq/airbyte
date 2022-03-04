#!/usr/bin/env bash
# THIS INSTALL SCRIPT IS A WORK IN PROGRESS
# It currently only works for ZSH and Bash profiles, and does not check for previous install.
# It creates an octavia alias in ~/.zshrc bound to a docker run command
set -e
VERSION=dev

detect_profile() {
    if [ "${SHELL#*bash}" != "$SHELL" ]; then
        if [ -f "$HOME/.bashrc" ]; then
        DETECTED_PROFILE="$HOME/.bashrc"
        elif [ -f "$HOME/.bash_profile" ]; then
        DETECTED_PROFILE="$HOME/.bash_profile"
        fi
    elif [ "${SHELL#*zsh}" != "$SHELL" ]; then
        if [ -f "$HOME/.zshrc" ]; then
        DETECTED_PROFILE="$HOME/.zshrc"
        fi
    fi

    if [ -z "${DETECTED_PROFILE}" ]; then
        echo "Cannot install! This scripts only works if you are using one of these profiles: ~/.bashrc, ~/.bash_profile or ~/.zshrc"
        exit 1
    else
        echo "octavia alias will be added to ${DETECTED_PROFILE}"
    fi
}

check_docker_is_running() {
    if ! docker info > /dev/null 2>&1; then
    echo "This script uses docker, and it isn't running - please start docker and try again!"
    exit 1
    fi
}

delete_previous_alias() {
    sed -i'' -e '/^alias octavia=/d' ${DETECTED_PROFILE}
}

pull_image() {
    docker pull airbyte/octavia-cli:${VERSION}
}

add_alias() {
    echo 'alias octavia="pwd | xargs -I {} docker run --rm -v {}:/home/octavia-project --network host -e AIRBYTE_URL="${AIRBYTE_URL}" -e AIRBYTE_WORKSPACE_ID="${AIRBYTE_WORKSPACE_ID}" airbyte/octavia-cli:'${VERSION}'"'  >> ~/.zshrc
    echo "octavia alias was added to ${DETECTED_PROFILE} , please open a new terminal window or run source ${DETECTED_PROFILE}"
}

install () {
    check_docker_is_running
    detect_profile
    set -u
    # pull_image # uncomment this when we publish the image to our docker registry
    delete_previous_alias
    add_alias
}

install

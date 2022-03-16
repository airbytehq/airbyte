#!/usr/bin/env bash

# This install scripts currently only works for ZSH and Bash profiles.
# It creates an octavia alias in your profile bound to a docker run command

VERSION=0.1.0
OCTAVIA_ENV_FILE=${HOME}/.octavia

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
        echo "🚨 - Cannot install! This scripts only works if you are using one of these profiles: ~/.bashrc, ~/.bash_profile or ~/.zshrc"
        exit 1
    else
        echo "octavia alias will be added to ${DETECTED_PROFILE}"
    fi
}

check_docker_is_running() {
    if ! docker info > /dev/null 2>&1; then
    echo "🚨 - This script uses docker, and it isn't running - please start docker and try again!"
    exit 1
    fi
}

delete_previous_alias() {
  sed -i'' -e '/^alias octavia=/d' ${DETECTED_PROFILE}
}


pull_image() {
    docker pull airbyte/octavia-cli:${VERSION} > /dev/null 2>&1
}

add_octavia_comment_to_profile() {
    printf "\n# OCTAVIA CLI\n" >> ${DETECTED_PROFILE}
}

create_octavia_env_file() {
    echo "OCTAVIA_ENV_FILE=${OCTAVIA_ENV_FILE}"  >> ${DETECTED_PROFILE}
    touch ${OCTAVIA_ENV_FILE}
    echo "🐙 - 💾 The octavia env file was created at ${OCTAVIA_ENV_FILE}"
}


add_alias() {
    echo 'alias octavia="pwd | xargs -o -I {} docker run -i --rm -v {}:/home/octavia-project --network host --env-file \${OCTAVIA_ENV_FILE} airbyte/octavia-cli:'${VERSION}'"'  >> ${DETECTED_PROFILE}
    echo "🐙 - 🎉 octavia alias was added to ${DETECTED_PROFILE}, please open a new terminal window or run source ${DETECTED_PROFILE}"
}

install() {
    pull_image
    add_alias
}

update_or_install() {
    if grep -q "^alias octavia=*" ${DETECTED_PROFILE}; then
        read -p "❓ - You already have an octavia alias in your profile. Do you want to update? (Y/n)" -n 1 -r </dev/tty
        echo    # (optional) move to a new line
        if [[ $REPLY =~ ^[Yy]$ ]]
        then
            delete_previous_alias
            install
        fi
    else
        add_octavia_comment_to_profile
        create_octavia_env_file
        install
    fi
}

set -e
check_docker_is_running
detect_profile
set -u
update_or_install

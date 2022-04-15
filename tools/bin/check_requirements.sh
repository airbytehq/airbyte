#!/usr/bin/env bash

# Ensure always run from this directory because it uses relative paths
cd "$(dirname "${0}")" || exit 1

echo "Checking Airbyte development tools and versions.."

printf "\n";
DESIRED_JAVA_VERSION="$(cat ../../.java-version)"
printf "Java ";
if [[ "$(which java)" && "$(java --version)" ]];
    then
        str="$(java --version)"
        # Returns like "openjdk 11.0.12 2021-11-24"
        IFS=' ' read -ra array <<< "${str}"
        java_version="${array[1]}"
        printf "${java_version} is installed"
        if [[ "${java_version}" == "${DESIRED_JAVA_VERSION}" ]];
            then
                printf " and matches version ${DESIRED_JAVA_VERSION}"
            else
                printf " but does not match version ${DESIRED_JAVA_VERSION}, you might see unexpected behavior"
        fi
    else
        printf "not installed, please install Java ${DESIRED_JAVA_VERSION}"
fi;

#printf "\n";
#DESIRED_PIP_VERSION="$(cat ../../.pip-version)"
#printf "Pip ";
#if [[ "$(which pip)" && "$(pip --version)" ]];
#    then
#        str="$(pip --version)"
#        # Returns like "pip 20.X.Y from.."
#        IFS=' ' read -ra array <<< "${str}"
#        pip_version="${array[1]}"
#        printf "${pip_version} is installed"
#        if [[ "${pip_version}" == "${DESIRED_PIP_VERSION}" ]];
#            then
#                printf " and matches version ${DESIRED_PIP_VERSION}"
#            else
#                printf " but does not match version ${DESIRED_PIP_VERSION}, you might see unexpected behavior"
#        fi
#    else
#        printf "not installed, please install Pip ${DESIRED_PIP_VERSION}"
#fi;

printf "\n";
printf "Python ";
DESIRED_PYTHON_VERSION="$(cat ../../.python-version)"
if [[ -n "$(which python3)" && -n "$(python3 --version)" ]];
    then
        str="$(python3 --version)"
        # Returns like "Python 3.9.9"
        IFS=' ' read -ra array <<< "${str}"
        python_version="${array[1]}"
        printf "${python_version} is installed"
        if [[ "${python_version}" == "${DESIRED_PYTHON_VERSION}" ]];
            then
                printf " and matches version ${DESIRED_PYTHON_VERSION}"
            else
                printf " but does not match version ${DESIRED_PYTHON_VERSION}, you might see unexpected behavior"
        fi
    else
        printf "not installed, please install Python ${DESIRED_PYTHON_VERSION}"
fi;

printf "\n";
DESIRED_NODE_VERSION="$(cat ../../.node-version)"
printf "Node ";
if [[ "$(which node)" && "$(node --version)" ]];
    then
        node_version="$(node --version | tr -d v)"
        # Returns like v16.13.0, strip the "v"
        printf "${node_version} is installed"
        if [[ "${node_version}" == "${DESIRED_NODE_VERSION}" ]];
            then
                printf " and matches version ${DESIRED_NODE_VERSION}"
            else
                printf " but does not match version ${DESIRED_NODE_VERSION}, you might see unexpected behavior"
        fi
    else
        printf "not installed, please install Node ${DESIRED_NODE_VERSION}"
fi;

printf "\n"
printf "Docker ";
# Currently no pinned docker version: https://github.com/airbytehq/airbyte/issues/9229
if [[ $(which docker) && $(docker --version) ]]; then
    printf "is installed"
  else
    printf "needs to be installed"
fi;

printf "\n";
printf "Docker Compose ";
# Currently no pinned docker-compose version: https://github.com/airbytehq/airbyte/issues/9229
if [[ $(which docker-compose) && $(docker-compose --version) ]]; then
    printf "is installed"
  else
    printf "needs to be installed"
fi;

printf "\n";
printf "JQ ";
# Currently no pinned jq version: https://github.com/airbytehq/airbyte/issues/9229
if [[ $(which jq) && $(jq --version) ]]; then
    printf "is installed"
  else
    printf "needs to be installed"
fi;
printf "\n";
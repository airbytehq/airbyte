#!/bin/bash
# Currently this assumes debian (buster)

set -e

apt-get update
apt-get --assume-yes install build-essential=12.6 \
                      libpq-dev=11.7-0+deb10u1 \
                      python3.7=3.7.3-2+deb10u2 \
                      python3-venv=3.7.3-1 \
                      python3-pip=18.1-5

. install_all_connectors.sh 

#!/bin/bash
# Currently this assumes debian (buster)

set -e

dpkg --configure -a
sudo apt-get install -f
apt-get -y clean
apt-get -y update
apt-get -y upgrade
apt-get -y install build-essential=12.4ubuntu1 \
  libpq-dev=10.12-0ubuntu0.18.04.1 \
  python3.7=3.7.3-2~18.04.1

. install_all_connectors.sh

#!/bin/bash
set -e

echo "Running destination-s3 docker custom steps..."

ARCH=$(uname -m)
if [ "$ARCH" == "x86_64" ] || [ "$ARCH" = "amd64" ]; then
  echo "$ARCH"
  yum install lzop lzo lzo-devel -y
fi

yum clean all

mkdir -p /data/job
chown -R airbyte:airbyte /data

mkdir -p /dest
chown -R airbyte:airbyte /dest


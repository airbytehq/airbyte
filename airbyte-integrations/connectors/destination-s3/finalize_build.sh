#!/bin/bash
set -e

echo "Running destination-s3 docker custom steps..."

ARCH=$(uname -m)

if [ "$ARCH" == "x86_64" ] || [ "$ARCH" = "amd64" ]; then
  echo "$ARCH"
  yum install lzop lzo lzo-dev -y
fi

yum clean all

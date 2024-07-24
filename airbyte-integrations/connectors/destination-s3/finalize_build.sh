#!/bin/bash
set -e

echo "Running destination-s3 docker custom steps..."

ARCH=$(uname -m)
echo "SGX $ARCH OK"

if [ "$ARCH" == "x86_64" ] || [ "$ARCH" = "amd64" ] || [ "$ARCH" = "aarch64" ]; then
  echo "$ARCH"
  yum install lzop lzo lzo-devel -y
else
  echo "can't install lzo for arch $ARCH!!"
fi

if [ "$ARCH" = "aarch64" ]; then
  cd /tmp &&
  mkdir unzipped &&
  cd unzipped &&
  unzip /airbyte/lib/hadoop-lzo-0.4.20.jar &&
  mv native/Linux-amd64-64 native/Linux-aarch64-64 &&
  zip -r ../hadoop-lzo-0.4.20.jar . &&
  rm /airbyte/lib/hadoop-lzo-0.4.20.jar &&
  cd .. &&
  mv  hadoop-lzo-0.4.20.jar /airbyte/lib/ &&
  rm -rf unzipped
fi

yum clean all

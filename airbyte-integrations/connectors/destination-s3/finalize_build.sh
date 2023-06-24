#!/bin/bash
set -e

ARCH=$(uname -m)

if [ "$ARCH" == "x86_64" ] || [ "$ARCH" = "amd64" ]; then
  echo "$ARCH"
  yum install lzop lzo lzo-dev -y

# alanechere: I'm not sure we need this custom install of lzo anymore. Using the yum install above works in the build context.
elif [ "$ARCH" == "aarch64" ] || [ "$ARCH" = "arm64" ]; then
  echo "$ARCH"
  yum group install -y "Development Tools"
  yum install lzop lzo lzo-dev wget curl unzip zip maven git which -y
  wget https://www.oberhumer.com/opensource/lzo/download/lzo-2.10.tar.gz -P /tmp
  cd /tmp
  tar xvfz lzo-2.10.tar.gz
  cd /tmp/lzo-2.10/
  ./configure --enable-shared --prefix=/usr/local/lzo-2.10
  make
  make install
  git clone https://github.com/twitter/hadoop-lzo.git /usr/lib/hadoop/lib/hadoop-lzo/
  curl -s "https://get.sdkman.io" | bash
  source /root/.sdkman/bin/sdkman-init.sh
  # alafanechere: The following command exits with 1, it makes the build fail.
  sdk install java 8.0.342-librca
  sdk use java 8.0.342-librca
  cd /usr/lib/hadoop/lib/hadoop-lzo/

  C_INCLUDE_PATH=/usr/local/lzo-2.10/include LIBRARY_PATH=/usr/local/lzo-2.10/lib mvn clean package
  find /usr/lib/hadoop/lib/hadoop-lzo/ -name '*libgplcompression*' -exec cp {} /usr/lib/ \;
  echo "AFTER FIND"

else
  echo "Unknown architecture"
fi

yum clean all

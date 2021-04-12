#!/bin/bash

set -euo pipefail

rm -rf /tmp/airbyte_crt
mkdir -p /tmp/airbyte_crt
cd /tmp/airbyte_crt

openssl req -new -text -passout pass:abcd -subj /CN=localhost -out server.req -keyout privkey.pem
openssl rsa -in privkey.pem -passin pass:abcd -out server.key
openssl req -x509 -in server.req -text -key server.key -out server.crt
chown 0:70 server.key
chmod 640 server.key

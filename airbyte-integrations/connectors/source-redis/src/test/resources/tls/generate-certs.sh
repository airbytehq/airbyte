#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")"
work="$(mktemp -d)"
trap 'rm -rf "$work"' EXIT

openssl genrsa -out ca.key 2048
openssl req -x509 -new -key ca.key -sha256 -days 36500 \
  -subj "/CN=Redis Test CA" -out ca.crt

openssl genrsa -out server.key 2048
openssl req -new -key server.key -subj "/CN=redis" -out "$work/server.csr"
printf '%s\n' \
  "basicConstraints=CA:FALSE" \
  "keyUsage=digitalSignature,keyEncipherment" \
  "extendedKeyUsage=serverAuth" \
  "subjectAltName=DNS:localhost,DNS:redis,IP:127.0.0.1" > "$work/server.ext"
openssl x509 -req -in "$work/server.csr" -CA ca.crt -CAkey ca.key \
  -CAcreateserial -days 36500 -sha256 -extfile "$work/server.ext" -out server.crt

openssl genrsa -out client.key 2048
openssl req -new -key client.key -subj "/CN=Redis Test Client" -out "$work/client.csr"
printf '%s\n' \
  "basicConstraints=CA:FALSE" \
  "keyUsage=digitalSignature,keyEncipherment" \
  "extendedKeyUsage=clientAuth" > "$work/client.ext"
openssl x509 -req -in "$work/client.csr" -CA ca.crt -CAkey ca.key \
  -CAcreateserial -days 36500 -sha256 -extfile "$work/client.ext" -out client.crt

openssl req -x509 -newkey rsa:2048 -nodes -keyout wrong-ca.key -out wrong-ca.crt \
  -sha256 -days 36500 -subj "/CN=Redis Wrong Test CA"

chmod 644 ca.key ca.crt server.key server.crt client.key client.crt wrong-ca.key wrong-ca.crt

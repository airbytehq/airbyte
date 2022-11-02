#!/bin/bash

set -o xtrace

# This is mostly based on https://github.com/confluentinc/cp-docker-images/blob/5.3.3-post/examples/kafka-cluster-ssl/secrets/create-certs.sh
# Differences:
#   trimmed down to just one broker + producer
#   added -noprompt flags so that it can run non-interactively
#   producer doesn't generate cert+keystores

# Create a certificate authority
openssl req -new -x509 -keyout snakeoil-ca-1.key -out snakeoil-ca-1.crt -days 365 -subj '/CN=ca1.test.confluent.io/OU=TEST/O=CONFLUENT/L=PaloAlto/S=Ca/C=US' -passin pass:confluent -passout pass:confluent

broker_hostname=$(hostname)

## Create certificate + creds for server (i.e. broker)
# Create keystores
keytool -genkey -noprompt \
        -alias broker1 \
        -dname "CN=${broker_hostname}, OU=TEST, O=CONFLUENT, L=PaloAlto, S=Ca, C=US" \
        -keystore kafka.broker1.keystore.jks \
        -keyalg RSA \
        -storepass confluent \
        -keypass confluent

# Create CSR, sign the key and import back into keystore
keytool -keystore kafka.broker1.keystore.jks -alias broker1 -certreq -file broker1.csr -storepass confluent -keypass confluent
# TODO
echo << EOF
[req]
default_bits  = 2048
distinguished_name = req_distinguished_name
req_extensions = req_ext
x509_extensions = v3_req
prompt = no

[req_distinguished_name]
countryName = US
stateOrProvinceName = Ca
localityName = PaloAlto
organizationName = CONFLUENT
commonName = 120.0.0.1: Self-signed certificate

[req_ext]
subjectAltName = @alt_names

[v3_req]
subjectAltName = @alt_names

[alt_names]
IP.1 = 172.17.0.3
EOF > san.cnf
# echo 'IP.1 = '$(awk '/\|--/ && !/\.0$|\.255$/ {print $2}' /proc/net/fib_trie | grep -v 127.0.0.1 | uniq | head -n 1) > san.cnf
openssl req -x509 -nodes -days 730 -newkey rsa:2048 -keyout key.pem -out cert.pem -config san.cnf
# openssl x509 -req -CA snakeoil-ca-1.crt -CAkey snakeoil-ca-1.key -in broker1.csr -out broker1-ca1-signed.crt -days 9999 -CAcreateserial -passin pass:confluent
keytool -keystore kafka.broker1.keystore.jks -alias CARoot -import -file snakeoil-ca-1.crt -storepass confluent -keypass confluent -noprompt
keytool -keystore kafka.broker1.keystore.jks -alias broker1 -import -file broker1-ca1-signed.crt -storepass confluent -keypass confluent

# Create truststore and import the CA cert.
keytool -keystore kafka.broker1.truststore.jks -alias CARoot -import -file snakeoil-ca-1.crt -storepass confluent -keypass confluent -noprompt

echo "confluent" > broker1_sslkey_creds
echo "confluent" > broker1_keystore_creds
echo "confluent" > broker1_truststore_creds

## Create truststore for client (i.e. producer)
# # Create keystores
# keytool -genkey -noprompt \
#         -alias producer \
#         -dname "CN=producer.test.confluent.io, OU=TEST, O=CONFLUENT, L=PaloAlto, S=Ca, C=US" \
#         -keystore kafka.producer.keystore.jks \
#         -keyalg RSA \
#         -storepass confluent \
#         -keypass confluent

# # Create CSR, sign the key and import back into keystore
# keytool -keystore kafka.producer.keystore.jks -alias producer -certreq -file producer.csr -storepass confluent -keypass confluent
# openssl x509 -req -CA snakeoil-ca-1.crt -CAkey snakeoil-ca-1.key -in producer.csr -out producer-ca1-signed.crt -days 9999 -CAcreateserial -passin pass:confluent
# keytool -keystore kafka.producer.keystore.jks -alias CARoot -import -file snakeoil-ca-1.crt -storepass confluent -keypass confluent
# keytool -keystore kafka.producer.keystore.jks -alias producer -import -file producer-ca1-signed.crt -storepass confluent -keypass confluent

# Create truststore, import the CA cert, and convert JKS -> PKCS12 -> PEM
keytool -keystore kafka.producer.truststore.jks -alias CARoot -import -file snakeoil-ca-1.crt -storepass confluent -keypass confluent -noprompt
keytool -importkeystore -srckeystore kafka.producer.truststore.jks -destkeystore kafka.producer.truststore.p12 -srcstoretype jks -deststoretype pkcs12 -noprompt -srcstorepass confluent -deststorepass confluent
openssl pkcs12 -in kafka.producer.truststore.p12 -out kafka.producer.truststore.pem -passin pass:confluent

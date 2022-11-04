#!/bin/bash

set -o xtrace
set -e

# This is mostly based on https://github.com/confluentinc/cp-docker-images/blob/5.3.3-post/examples/kafka-cluster-ssl/secrets/create-certs.sh
# Differences:
#   trimmed down to just one broker + producer
#   added -noprompt flags so that it can run non-interactively
#   producer doesn't generate cert+keystores

# Create a certificate authority
openssl req -new -x509 -keyout snakeoil-ca-1.key -out snakeoil-ca-1.crt -days 365 -subj '/CN=ca1.test.confluent.io/OU=TEST/O=CONFLUENT/L=PaloAlto/S=Ca/C=US' -passin pass:confluent -passout pass:confluent

broker_hostname=broker1.kafka.destinations.test.airbyte.com

# Create broker keystore
keytool -genkey -noprompt \
        -alias broker1 \
        -dname "CN=${broker_hostname}, OU=TEST, O=CONFLUENT, L=PaloAlto, S=Ca, C=US" \
        -keystore kafka.broker1.keystore.jks \
        -keyalg RSA \
        -storepass confluent \
        -keypass confluent

# get the broker's private key from keystore
keytool -importkeystore \
    -srckeystore kafka.broker1.keystore.jks \
    -destkeystore broker1.p12 \
    -deststoretype PKCS12 \
    -srcalias broker1 \
    -srcstorepass confluent \
    -deststorepass confluent \
    -destkeypass confluent
openssl pkcs12 -in broker1.p12  -nodes -nocerts -out broker1.pem -passin pass:confluent

# We need to add the broker's IP as a SAN because the test client connects via IP, so build a config file
local_ip=$(awk '/\|--/ && !/\.0$|\.255$/ {print $2}' /proc/net/fib_trie | grep -v 127.0.0.1 | uniq | head -n 1)
cat <<EOF > san.cnf
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
commonName = ${broker_hostname}

[req_ext]
subjectAltName = @alt_names

[v3_req]
subjectAltName = @alt_names

[alt_names]
IP.1 = ${local_ip}
DNS.1 = localhost
EOF

# Generate and sign the broker's certificate
openssl req -new -out broker1.csr -config san.cnf -key broker1.pem -passout pass:confluent
openssl x509 -req -in broker1.csr -CA snakeoil-ca-1.crt -CAkey snakeoil-ca-1.key -CAcreateserial -out broker1-ca1-signed.crt -passin pass:confluent -extfile san.cnf -extensions v3_req
# import the cert chain into the broker's keystore
keytool -keystore kafka.broker1.keystore.jks -alias CARoot -import -file snakeoil-ca-1.crt -storepass confluent -keypass confluent -noprompt
keytool -keystore kafka.broker1.keystore.jks -alias broker1 -import -file broker1-ca1-signed.crt -storepass confluent -keypass confluent

# the broker should trust itself
keytool -keystore kafka.broker1.truststore.jks -alias CARoot -import -file snakeoil-ca-1.crt -storepass confluent -keypass confluent -noprompt

echo "confluent" > broker1_sslkey_creds
echo "confluent" > broker1_keystore_creds
echo "confluent" > broker1_truststore_creds

# Create truststore for the producer and import the CA cert
keytool -keystore kafka.producer.truststore.jks -alias CARoot -import -file snakeoil-ca-1.crt -storepass confluent -keypass confluent -noprompt
# convert JKS -> PKCS12 -> PEM (because destination-kafka requires the PEM format)
keytool -importkeystore -srckeystore kafka.producer.truststore.jks -destkeystore kafka.producer.truststore.p12 -srcstoretype jks -deststoretype pkcs12 -noprompt -srcstorepass confluent -deststorepass confluent
openssl pkcs12 -in kafka.producer.truststore.p12 -out kafka.producer.truststore.pem -passin pass:confluent

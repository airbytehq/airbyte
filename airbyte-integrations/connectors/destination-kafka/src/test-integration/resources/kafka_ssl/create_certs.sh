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

## Create certificate + creds for server (i.e. broker)
# Create keystores
keytool -genkey -noprompt \
        -alias broker1 \
        -dname "CN=${broker_hostname}, OU=TEST, O=CONFLUENT, L=PaloAlto, S=Ca, C=US" \
        -keystore kafka.broker1.keystore.jks \
        -keyalg RSA \
        -storepass confluent \
        -keypass confluent

# We need to add the broker's IP as a SAN because the test client connects via IP
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
EOF
# get the broker's private key from keystore so that we can generate the crt using the correct key pair
keytool -importkeystore \
    -srckeystore kafka.broker1.keystore.jks \
    -destkeystore broker1.p12 \
    -deststoretype PKCS12 \
    -srcalias broker1 \
    -srcstorepass confluent \
    -deststorepass confluent \
    -destkeypass confluent
openssl pkcs12 -in broker1.p12  -nodes -nocerts -out broker1.pem -passin pass:confluent
# Generate and sign the certificate
openssl req -x509 -nodes -days 730 -new -key broker1.pem -passin pass:confluent -out broker1-ca1-signed.crt -config san.cnf
# import the cert chain into the broker's keystore
keytool -keystore kafka.broker1.keystore.jks -alias CARoot -import -file snakeoil-ca-1.crt -storepass confluent -keypass confluent -noprompt
keytool -keystore kafka.broker1.keystore.jks -alias broker1 -import -file broker1-ca1-signed.crt -storepass confluent -keypass confluent

echo "confluent" > broker1_sslkey_creds
echo "confluent" > broker1_keystore_creds

# Create truststore for the producer, import the CA cert, and convert JKS -> PKCS12 -> PEM
keytool -keystore kafka.producer.truststore.jks -alias CARoot -import -file snakeoil-ca-1.crt -storepass confluent -keypass confluent -noprompt
keytool -importkeystore -srckeystore kafka.producer.truststore.jks -destkeystore kafka.producer.truststore.p12 -srcstoretype jks -deststoretype pkcs12 -noprompt -srcstorepass confluent -deststorepass confluent
openssl pkcs12 -in kafka.producer.truststore.p12 -out kafka.producer.truststore.pem -passin pass:confluent

#!/bin/sh
set -eux;

# Installs the Amazon DocumentDB CA certificates into the default keystore
# Adapted from https://docs.aws.amazon.com/documentdb/latest/developerguide/connect_programmatically.html

# Default Java keystore password
storepassword=changeit

curl -sS "https://s3.amazonaws.com/rds-downloads/rds-combined-ca-bundle.pem" > rds-combined-ca-bundle.pem

# Break up the combined certificate into individual certificates
# The version of csplit in the container does not seem to support the match all {*} option. Workaround is to split
# 99 times, which is more than we need, while ignoring the return value errors.
set +e
csplit -f 'rds-ca-' -k rds-combined-ca-bundle.pem /-----BEGIN\ CERTIFICATE-----/ '{99}'
set -e

# Delete all empty split files
find . -name 'rds-ca-*' -size 0 -print0 | xargs -0 rm

# Import all of the individual ca certificates into the Java keystore
for CERT in ./rds-ca-*; do
  alias=$(openssl x509 -noout -text -in $CERT | perl -ne 'next unless /Subject:/; s/.*(CN=|CN = )//; print')
  echo "Importing $alias"
  keytool -import -file ${CERT} -alias "${alias}" -cacerts -storepass ${storepassword} -noprompt
  rm $CERT
done

rm rds-combined-ca-bundle.pem
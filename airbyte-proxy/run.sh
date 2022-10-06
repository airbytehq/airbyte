#!/bin/bash

rm /etc/nginx/nginx.conf

if [[ -z "${BASIC_AUTH_USERNAME}" ]]; then
  echo "BASIC_AUTH_USERNAME is not set, skipping nginx auth"

  ln -s /etc/nginx/nginx-no-auth.conf /etc/nginx/nginx.conf
else
  echo "BASIC_AUTH_USERNAME is set, requiring auth for user '$BASIC_AUTH_USERNAME'"

  # htpasswd for basic authentication
  rm -rf /etc/nginx/.htpasswd
  htpasswd -c -b /etc/nginx/.htpasswd $BASIC_AUTH_USERNAME $BASIC_AUTH_PASSWORD

  ln -s /etc/nginx/nginx-auth.conf /etc/nginx/nginx.conf
fi

echo "starting nginx..."
nginx -g "daemon off;"

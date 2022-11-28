#!/bin/bash

rm /etc/nginx/nginx.conf

if [[ -z "${BASIC_AUTH_USERNAME}" ]]; then
  echo "BASIC_AUTH_USERNAME is not set, skipping nginx auth"

  TEMPLATE_PATH="/etc/nginx/templates/nginx-no-auth.conf.template"
else
  echo "BASIC_AUTH_USERNAME is set, requiring auth for user '$BASIC_AUTH_USERNAME'"

  # htpasswd for basic authentication
  rm -rf /etc/nginx/.htpasswd
  htpasswd -c -b /etc/nginx/.htpasswd $BASIC_AUTH_USERNAME $BASIC_AUTH_PASSWORD

  TEMPLATE_PATH="/etc/nginx/templates/nginx-auth.conf.template"
fi

envsubst '${PROXY_PASS_WEB} ${PROXY_PASS_API} ${CONNECTOR_BUILDER_SERVER_API} ${PROXY_PASS_RESOLVER} ${BASIC_AUTH_PROXY_TIMEOUT}' < $TEMPLATE_PATH > /etc/nginx/nginx.conf

echo "starting nginx..."
nginx -v
nginx -g "daemon off;"

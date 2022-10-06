#!/bin/sh

# htpasswd for basic authentication
rm -rf /etc/nginx/.htpasswd
htpasswd -c -b /etc/nginx/.htpasswd $BASIC_AUTH_USERNAME $BASIC_AUTH_PASSWORD

echo "starting nginx..."
nginx -g "daemon off;"

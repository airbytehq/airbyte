#! /usr/bin/env sh
set -e

/uwsgi-nginx-entrypoint.sh

# Get the URL for static files from the environment variable
USE_STATIC_URL=${STATIC_URL:-'/static'}
# Get the absolute path of the static files from the environment variable
USE_STATIC_PATH=${STATIC_PATH:-'/app/static'}
# Get the listen port for Nginx, default to 80
USE_LISTEN_PORT=${LISTEN_PORT:-80}

if [ -f /app/nginx.conf ]; then
    cp /app/nginx.conf /etc/nginx/nginx.conf
else
    content_server='server {\n'
    content_server=$content_server"    listen ${USE_LISTEN_PORT};\n"
    content_server=$content_server'    location / {\n'
    content_server=$content_server'        try_files $uri @app;\n'
    content_server=$content_server'    }\n'
    content_server=$content_server'    location @app {\n'
    content_server=$content_server'        include uwsgi_params;\n'
    content_server=$content_server'        uwsgi_pass unix:///tmp/uwsgi.sock;\n'
    content_server=$content_server'    }\n'
    content_server=$content_server"    location $USE_STATIC_URL {\n"
    content_server=$content_server"        alias $USE_STATIC_PATH;\n"
    content_server=$content_server'    }\n'
    # If STATIC_INDEX is 1, serve / with /static/index.html directly (or the static URL configured)
    if [ "$STATIC_INDEX" = 1 ] ; then
        content_server=$content_server'    location = / {\n'
        content_server=$content_server"        index $USE_STATIC_URL/index.html;\n"
        content_server=$content_server'    }\n'
    fi
    content_server=$content_server'}\n'
    # Save generated server /etc/nginx/conf.d/nginx.conf
    printf "$content_server" > /etc/nginx/conf.d/nginx.conf
fi

# For Alpine:
# Explicitly add installed Python packages and uWSGI Python packages to PYTHONPATH
# Otherwise uWSGI can't import Flask
if [ -n "$ALPINEPYTHON" ] ; then
    export PYTHONPATH=$PYTHONPATH:/usr/local/lib/$ALPINEPYTHON/site-packages:/usr/lib/$ALPINEPYTHON/site-packages
fi

exec "$@"
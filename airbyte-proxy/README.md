# Airbyte Proxy

This service uses Nginx to front the Aribyte `webapp` and `server` services to add Authentication via HTTP basic auth.

Authentication is controlled by 2 environment variables, `BASIC_AUTH_USERNAME` and `BASIC_AUTH_PASSWORD` which can be modified in the `.env` file for your Airbyte deployment. You can disable authentication by setting both `BASIC_AUTH_USERNAME` and `BASIC_AUTH_PASSWORD` to empty strings. Changes in your environment variables will be applied when the service (re)boots.

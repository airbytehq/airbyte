# Airbyte Proxy

This service uses Nginx to front the Aribyte `webapp` and `server` services to add Authentication via HTTP basic auth.

Authentication is controlled by 2 environment variables, `BASIC_AUTH_USERNAME` and `BASIC_AUTH_PASSWORD` which can be modified in the `.env` file for your Airbyte deployment. You can disable authentication by setting both `BASIC_AUTH_USERNAME` and `BASIC_AUTH_PASSWORD` to empty strings. Changes in your environment variables will be applied when the service (re)boots.

This service is intended to work in conjunction with the `airbyte_internal` network defined in the default docker compose file. By default, this application forwards requesting coming in on 8000 and 8001 to the PROXY_PASS_WEB and PROXY_PASS_API accordingly - which are also configured by environment variables within this container (see Dockerfile). The deafults are configured to work with the default `docker-compose.yaml` file for Airbyte OSS deployments.

```
ENV PROXY_PASS_WEB "http://airbyte-webapp:80"
ENV PROXY_PASS_API "http://airbyte-server:8001"
```

🐙

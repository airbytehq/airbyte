FROM airbyte/source-always-works:dev

WORKDIR /airbyte/integration_code

ENTRYPOINT ["./socat.sh"]

LABEL io.airbyte.version=0.1.0
LABEL io.airbyte.name=airbyte/source-always-works-socat-shim

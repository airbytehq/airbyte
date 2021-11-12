FROM node:14-alpine

ARG UID
ARG GID
ENV ENV_UID $UID
ENV ENV_GID $GID
ENV DOCS_DIR "/airbyte/docs/integrations"
ENV CONFIG_DIR "/airbyte/airbyte-config/init/src/main/resources/config"

RUN mkdir -p /airbyte
WORKDIR /airbyte/airbyte-integrations/connector-templates/generator

CMD npm install --silent --no-update-notifier && echo "INSTALL DONE" && \
    npm run generate "$package_desc" "$package_name" && \
    LAST_CREATED_CONNECTOR=$(ls -td /airbyte/airbyte-integrations/connectors/* | head -n 1) && \
    echo "chowning generated directory: $LAST_CREATED_CONNECTOR" && \
    chown -R $ENV_UID:$ENV_GID $LAST_CREATED_CONNECTOR/* && \
    echo "chowning docs directory: $DOCS_DIR" && \
    chown -R $ENV_UID:$ENV_GID $DOCS_DIR/* && \
    echo "chowning config directory: $CONFIG_DIR" && \
    chown -R $ENV_UID:$ENV_GID $CONFIG_DIR/*

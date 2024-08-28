FROM node:16-alpine

ARG UID
ARG GID
ENV ENV_UID $UID
ENV ENV_GID $GID
ENV DOCS_DIR "/airbyte/docs/integrations"

RUN mkdir -p /airbyte
WORKDIR /airbyte/airbyte-integrations/connector-templates/generator

CMD npm install --silent --no-update-notifier && echo "INSTALL DONE" && \
    npm run generate "$package_desc" "$package_name" && \
    LAST_CREATED_CONNECTOR=$(ls -td /airbyte/airbyte-integrations/connectors/* | head -n 1) && \
    echo "chowning generated directory: $LAST_CREATED_CONNECTOR" && \
    chown -R $ENV_UID:$ENV_GID $LAST_CREATED_CONNECTOR/* && \
    echo "chowning docs directory: $DOCS_DIR" && \
    chown -R $ENV_UID:$ENV_GID $DOCS_DIR/*

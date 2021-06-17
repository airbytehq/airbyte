FROM node:14-alpine

ARG UID
ARG GID
ENV ENV_UID $UID
ENV ENV_GID $GID

RUN mkdir -p /airbyte
WORKDIR /airbyte/airbyte-integrations/connector-templates/generator

CMD npm install --silent --no-update-notifier && \
    npm run generate "$package_desc" "$package_name" && \
    chown -R $ENV_UID:$ENV_GID /airbyte/*

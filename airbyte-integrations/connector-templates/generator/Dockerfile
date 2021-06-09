FROM node:14-alpine

ARG UID
ARG GID
ENV ENV_UID $UID
ENV ENV_GID $GID

RUN mkdir -p /airbyte
WORKDIR /airbyte/airbyte-integrations/connector-templates/generator

RUN npm install npm@7 --silent --no-update-notifier
CMD npm run generate && chown -R $ENV_UID:$ENV_GID /airbyte/*

FROM node:14-alpine

RUN mkdir -p /airbyte-integrations/connectors /airbyte-integrations/connector-templates/generator
WORKDIR /airbyte-integrations/connector-templates/generator

RUN npm install npm@7 --silent --no-update-notifier
CMD npm run generate

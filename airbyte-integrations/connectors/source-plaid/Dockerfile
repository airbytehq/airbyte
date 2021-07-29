# node 14
FROM node:alpine3.12

WORKDIR /airbyte/integration_code
# Copy source files
COPY package.json .
COPY source.js .
COPY spec.json .
# Install any needed dependencies
RUN npm install

ENV AIRBYTE_ENTRYPOINT "node /airbyte/integration_code/source.js"
ENTRYPOINT ["node", "/airbyte/integration_code/source.js"]

LABEL io.airbyte.version=0.2.1
LABEL io.airbyte.name=airbyte/source-plaid

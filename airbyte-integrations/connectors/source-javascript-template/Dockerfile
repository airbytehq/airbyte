# node 14
FROM node:alpine3.12

WORKDIR /airbyte/integration_code
# Copy source files
COPY package.json .
COPY source.js .
COPY spec.json .
# Install any needed dependencies
RUN npm install

ENTRYPOINT ["node", "/airbyte/integration_code/source.js"]

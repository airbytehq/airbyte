FROM node:14-alpine

RUN npm install broken-link-checker -g

ENTRYPOINT ["blc"]

LABEL io.airbyte.version=0.1.0
LABEL io.airbyte.name=airbyte/tool-link-checker
FROM node:14-alpine

RUN mkdir /connectors /sources
WORKDIR /sources/generator

RUN npm install npm@7 --silent --no-update-notifier
CMD npm run generate
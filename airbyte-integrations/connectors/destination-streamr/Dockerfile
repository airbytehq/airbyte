FROM node:14-alpine

WORKDIR /home/node/airbyte
# RUN npm install -g yarn

RUN apk add --no-cache --virtual .gyp \
   python3 \
   make \
   g++
# RUN apk add --update python make g++ \
#    && rm -rf /var/cache/apk/*

COPY lerna.json .tsconfig.json package.json yarn.lock ./
RUN sed -i "/eslint\|husky\|jest\|lint-staged\|mockttp\|prettier/d" package.json

COPY ./destinations ./destinations
RUN yarn
RUN yarn build

RUN apk del .gyp

ARG path
RUN test -n "$path" || (echo "'path' argument is not set, e.g --build-arg path=destinations/faros-destination" && false)
ENV CONNECTOR_PATH $path

RUN ln -s "/home/node/airbyte/$CONNECTOR_PATH/bin/main" "/home/node/airbyte/main"

ENV AIRBYTE_ENTRYPOINT "/home/node/airbyte/main"
ENTRYPOINT ["/home/node/airbyte/main"]

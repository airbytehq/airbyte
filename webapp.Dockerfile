# Cache node modules
FROM node:14.7-alpine AS cache

WORKDIR /code

COPY conduit-webapp/package.json conduit-webapp/package-lock.json ./
RUN npm install

# Build webapp
FROM node:14.7-alpine AS build

WORKDIR /code

COPY --from=cache /code/node_modules /code/node_modules
COPY conduit-webapp /code
RUN npm run-script build

# Build final image
FROM nginx:1.19-alpine

EXPOSE 8000

COPY --from=build /code/build /usr/share/nginx/html

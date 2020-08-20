# Cache build
FROM dataline/webapp-base:dev AS build

# Build final image
FROM nginx:1.19-alpine

EXPOSE 80

COPY --from=build /code/build /usr/share/nginx/html

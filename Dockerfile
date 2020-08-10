# BUILD
FROM gradle:jdk14 AS build

COPY . /code
WORKDIR /code
RUN gradle distTar --no-daemon

# RUN
FROM openjdk:14.0.2-slim
EXPOSE 8080

WORKDIR /app/conduit-server

# TODO: add data mount instead
RUN mkdir data

COPY --from=build /code/conduit-server/build/distributions/*.tar conduit-server.tar
RUN tar xf conduit-server.tar --strip-components=1

CMD bin/conduit-server

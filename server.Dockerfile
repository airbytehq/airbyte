# Prepare gradle dependency cache
FROM gradle:jdk14 AS cache

WORKDIR /code

# for i in **/*.gradle; do echo COPY ./$i $(dirname $i)/; done
COPY ./.env ./
COPY ./build.gradle ./
COPY ./dataline-api/build.gradle dataline-api/
COPY ./dataline-commons/build.gradle dataline-commons/
COPY ./dataline-server/build.gradle dataline-server/
COPY ./settings.gradle ./

RUN gradle --gradle-user-home=/tmp/gradle_cache clean dependencies --no-daemon

# Build artifact
FROM gradle:jdk14 AS build

WORKDIR /code

# TODO: add data mount instead
RUN mkdir data

COPY --from=cache /tmp/gradle_cache /home/gradle/.gradle
COPY . /code
RUN gradle clean distTar --no-daemon
RUN ls /code/dataline-server/build/distributions/

# Build final image
FROM openjdk:14.0.2-slim

EXPOSE 8000

WORKDIR /app/dataline-server

COPY --from=build /code/dataline-server/build/distributions/*.tar dataline-server.tar
RUN tar xf dataline-server.tar --strip-components=1

CMD bin/dataline-server

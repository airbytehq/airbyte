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

COPY --from=cache /tmp/gradle_cache /home/gradle/.gradle
COPY . /code
RUN gradle clean distTar --no-daemon
RUN ls /code/dataline-server/build/distributions/

# Build final image
FROM openjdk:14.0.2-slim

EXPOSE 8000

WORKDIR /app/dataline-server

# TODO: add data mount instead
RUN mkdir data

COPY --from=build /code/dataline-server/build/distributions/*.tar dataline-server.tar
RUN tar xf dataline-server.tar --strip-components=1

# add docker-compose-wait tool
ENV WAIT_VERSION 2.7.2
ADD https://github.com/ufoscout/docker-compose-wait/releases/download/$WAIT_VERSION/wait wait
RUN chmod +x wait

# wait for postgres to become available before starting server
CMD ./wait && bin/dataline-server

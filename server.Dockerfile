# Prepare gradle dependency cache
FROM gradle:jdk14 AS cache

WORKDIR /code

# for i in **/*.gradle; do echo COPY ./$i $(dirname $i)/; done
COPY ./build.gradle ./
COPY ./dataline-api/build.gradle dataline-api/
COPY ./dataline-commons/build.gradle dataline-commons/
COPY ./dataline-config-persistence/build.gradle dataline-config-persistence/
COPY ./dataline-config/build.gradle dataline-config/
COPY ./dataline-db/build.gradle dataline-db/
COPY ./dataline-server/build.gradle dataline-server/
COPY ./dataline-webapp/build.gradle dataline-webapp/
COPY ./dataline-workers/build.gradle dataline-workers/
COPY ./settings.gradle ./
COPY ./.env ./

RUN gradle --gradle-user-home=/tmp/gradle_cache clean dependencies --no-daemon

# Build artifact
FROM gradle:jdk14 AS build

WORKDIR /code

COPY --from=cache /tmp/gradle_cache /home/gradle/.gradle
COPY . /code
RUN ./tools/singer/setup_singer_env.buster.sh
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

## Begin Singer
## postgres taps need postgres binaries & build-base (gcc)
#RUN apt update && apt-get libpq-dev=11.7-0+deb10u1 build-essential=12.6 \
#    && ./tools/singer/install_connector.sh tap-postgres tap-postgres 0.1.0 \
#    && ./tools/singer/install_connector.sh target-postgres singer-target-postgres 0.2.4
## End singer
CMD bin/dataline-server

# Prepare gradle dependency cache
FROM gradle:jdk14 AS cache

WORKDIR /code

# for i in **/*.gradle; do echo COPY ./$i $(dirname $i)/; done
COPY ./.version ./
COPY ./build.gradle ./
COPY ./conduit-api/build.gradle conduit-api/
COPY ./conduit-commons/build.gradle conduit-commons/
COPY ./conduit-server/build.gradle conduit-server/
COPY ./conduit-ui/build.gradle conduit-ui/
COPY ./settings.gradle ./

RUN gradle --gradle-user-home=/tmp/gradle_cache clean dependencies --no-daemon

# Build artifact
FROM gradle:jdk14 AS build

WORKDIR /code

COPY --from=cache /tmp/gradle_cache /home/gradle/.gradle
COPY . /code
RUN gradle clean distTar --no-daemon
RUN ls /code/conduit-server/build/distributions/

# Build final image
FROM openjdk:14.0.2-slim

EXPOSE 8000

WORKDIR /app/conduit-server

COPY --from=build /code/conduit-server/build/distributions/*.tar conduit-server.tar
RUN tar xf conduit-server.tar --strip-components=1

CMD bin/conduit-server

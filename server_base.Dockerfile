# Prepare gradle dependency cache
FROM openjdk:14.0.2-slim AS cache

WORKDIR /code

# for i in **/*.gradle; do echo COPY ./$i $(dirname $i)/; done
COPY ./build.gradle ./
COPY ./dataline-api/build.gradle dataline-api/
COPY ./dataline-commons/build.gradle dataline-commons/
COPY ./dataline-config-persistence/build.gradle dataline-config-persistence/
COPY ./dataline-config/build.gradle dataline-config/
COPY ./dataline-db/build.gradle dataline-db/
COPY ./dataline-server/build.gradle dataline-server/
COPY ./dataline-workers/build.gradle dataline-workers/
COPY ./settings.gradle ./
COPY ./.env ./
# Since we're not inheriting the gradle image, easiest way to run gradle is via the wrapper.
COPY ./gradlew ./
COPY ./gradle ./gradle

RUN ./gradlew --gradle-user-home=/tmp/gradle_cache clean dependencies --no-daemon

# Build artifact
FROM openjdk:14.0.2-slim

WORKDIR /code

# Setup singer environment. Since this is an expensive operation, we run it as early as possible in the build stage.
COPY ./.env ./
COPY ./.root ./
COPY ./tools ./tools/
RUN mkdir -p /usr/local/lib/singer
RUN ./tools/singer/setup_singer_env.buster.sh /usr/local/lib/singer

# Install Node. While the UI is not going to be served from this container, running UI tests is part of the build.
RUN apt-get update \
    && apt-get install -y curl \
    && curl -sL https://deb.nodesource.com/setup_14.x | bash - \
    && apt-get install -y nodejs

COPY --from=cache /tmp/gradle_cache /home/gradle/.gradle
COPY . /code

# Create distributions, but don't run tests just yet
RUN ./gradlew clean distTar --no-daemon --console rich
ENTRYPOINT ["./gradlew", "build", "--no-daemon", "--console", "rich"]


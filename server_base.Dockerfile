# Build artifact
FROM openjdk:14.0.2-slim

WORKDIR /code

# Setup singer environment. Since this is an expensive operation, we run it as early as possible in the build stage.
COPY ./.env ./
COPY ./.root ./
COPY ./tools/singer ./tools/singer
COPY ./tools/lib ./tools/lib
RUN mkdir -p /usr/local/lib/singer
RUN ./tools/singer/setup_singer_env.buster.sh /usr/local/lib/singer

# Install Node. While the UI is not going to be served from this container, running UI tests is part of the build.
RUN apt-get update \
    && apt-get install -y curl \
    && curl -sL https://deb.nodesource.com/setup_14.x | bash - \
    && apt-get install -y nodejs

COPY . /code

# Create distributions, but don't run tests just yet
RUN ./gradlew clean distTar --no-daemon --console rich
ENTRYPOINT ["./gradlew", "build", "--no-daemon", "--console", "rich"]


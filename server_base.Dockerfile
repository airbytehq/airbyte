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

# Cache Gradle executable
WORKDIR /code
COPY ./gradlew .
COPY ./gradle ./gradle
RUN ./gradlew build --console=plain --no-daemon

# Copy code, node_modules, etc.
COPY . /code

# Create distributions
RUN ./gradlew clean distTar build -x test --console=plain --no-daemon --console rich -g /home/gradle/.gradle

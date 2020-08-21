# Build artifact
FROM openjdk:14.0.2-slim

WORKDIR /code

# Setup singer environment. Since this is an expensive operation, we run it as early as possible in the build stage.
COPY ./.env ./
COPY ./.root ./
COPY ./tools/lib ./tools/lib

# Cache Gradle executable
WORKDIR /code
COPY ./gradlew .
COPY ./gradle ./gradle
RUN ./gradlew build --no-daemon

# Copy code, node_modules, etc.
COPY . /code

# Create distributions
RUN ./gradlew clean distTar build -x test --no-daemon -g /home/gradle/.gradle

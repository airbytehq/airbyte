# Build artifact
FROM openjdk:14.0.2-slim

WORKDIR /code

# Cache Gradle executable
COPY ./gradlew .
COPY ./gradle ./gradle
RUN ./gradlew build --no-daemon

# Copy code, etc.
COPY . /code

# Create distributions
RUN ./gradlew clean distTar build -x test --no-daemon -g /home/gradle/.gradle

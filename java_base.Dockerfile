FROM openjdk:14.0.2-slim

WORKDIR /code

# Cache Gradle executable
COPY ./gradlew ./
COPY ./gradle ./gradle
RUN ./gradlew build --no-daemon

# Create distributions
RUN ./gradlew clean distTar build -x test --no-daemon -g /home/gradle/.gradle

FROM openjdk:14.0.2-slim

WORKDIR /code

# Cache Gradle executable
COPY ./gradlew .
COPY ./gradle ./gradle
RUN ./gradlew build --no-daemon -g /home/gradle/.gradle

# Copy code, etc.
COPY . /code

RUN ./gradlew clean distTar build -x test -x dataline-webapp --no-daemon -g /home/gradle/.gradle

FROM ubuntu:20.04 AS build-base

# Install tools
RUN apt-get update && apt-get -y install curl

# Setup Node & Java
RUN curl -sL https://deb.nodesource.com/setup_14.x | bash -
RUN apt-get update && apt-get -y install \
  nodejs \
  openjdk-14-jdk

FROM build-base AS build

WORKDIR /code

# Cache Gradle executable
COPY ./gradlew .
COPY ./gradle ./gradle
RUN ./gradlew build --no-daemon -g /home/gradle/.gradle

# Copy code, etc.
COPY . /code

RUN ./gradlew clean distTar build -x test --no-daemon -g /home/gradle/.gradle

# BUILD
FROM gradle:jdk14 AS build

COPY . /code
WORKDIR /code
RUN gradle fatjar --no-daemon

# RUN
FROM openjdk:14.0.2-slim

RUN mkdir /app

COPY --from=build /code/build/libs/*fatjar*.jar /app/conduit-application.jar

ENTRYPOINT ["java", "-jar", "/app/conduit-application.jar"]

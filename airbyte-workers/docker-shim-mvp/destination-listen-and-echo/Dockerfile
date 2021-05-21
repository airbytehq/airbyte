# Use the same java base to simulate a destination image.
#FROM airbyte/integration-base-java:dev
FROM debian:latest
ENV AIRBYTE_ENTRYPOINT="./listen-and-echo.sh"

RUN apt-get update && apt-get install -y bash socat && rm -rf /var/lib/apt/lists/*

WORKDIR /airbyte/integration_code

COPY listen-and-echo.sh ./

ENTRYPOINT ["./listen-and-echo.sh"]

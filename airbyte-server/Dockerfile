FROM openjdk:14.0.2-slim AS server

EXPOSE 8000

ENV APPLICATION airbyte-server

WORKDIR /app

COPY build/distributions/${APPLICATION}-0*.tar ${APPLICATION}.tar

RUN tar xf ${APPLICATION}.tar --strip-components=1

# wait for upstream dependencies to become available before starting server
ENTRYPOINT ["/bin/bash", "-c", "bin/${APPLICATION}"]

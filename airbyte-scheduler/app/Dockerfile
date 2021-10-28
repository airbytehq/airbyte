ARG JDK_VERSION=14.0.2
FROM openjdk:${JDK_VERSION}-slim AS scheduler

ENV APPLICATION airbyte-scheduler

WORKDIR /app

COPY build/distributions/${APPLICATION}-0*.tar ${APPLICATION}.tar

RUN tar xf ${APPLICATION}.tar --strip-components=1

# wait for upstream dependencies to become available before starting server
ENTRYPOINT ["/bin/bash", "-c", "bin/${APPLICATION}"]

ARG JDK_VERSION=14.0.2
FROM openjdk:${JDK_VERSION}-slim AS migrate

ENV APPLICATION airbyte-migration

WORKDIR /app

# Move and run scheduler
COPY bin/${APPLICATION}-0.32.5-alpha.tar ${APPLICATION}.tar

RUN tar xf ${APPLICATION}.tar --strip-components=1

# wait for upstream dependencies to become available before starting server
ENTRYPOINT ["/bin/bash", "-c", "bin/${APPLICATION} $@"]

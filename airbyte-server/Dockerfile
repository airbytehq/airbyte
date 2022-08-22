ARG JDK_VERSION=19-slim-bullseye
ARG JDK_IMAGE=openjdk:${JDK_VERSION}
FROM ${JDK_IMAGE} AS server

EXPOSE 8000

ARG VERSION=0.40.0-alpha

ENV APPLICATION airbyte-server
ENV VERSION ${VERSION}

WORKDIR /app

# This is automatically unzipped by Docker
ADD bin/${APPLICATION}-${VERSION}.tar /app

# wait for upstream dependencies to become available before starting server
ENTRYPOINT ["/bin/bash", "-c", "${APPLICATION}-${VERSION}/bin/${APPLICATION}"]

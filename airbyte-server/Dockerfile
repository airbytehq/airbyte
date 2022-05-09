ARG JDK_VERSION=17.0.1
FROM openjdk:${JDK_VERSION}-slim AS server

EXPOSE 8000

ARG VERSION=0.37.0-alpha

ENV APPLICATION airbyte-server
ENV VERSION ${VERSION}

WORKDIR /app

ADD bin/${APPLICATION}-${VERSION}.tar /app

# wait for upstream dependencies to become available before starting server
ENTRYPOINT ["/bin/bash", "-c", "${APPLICATION}-${VERSION}/bin/${APPLICATION}"]

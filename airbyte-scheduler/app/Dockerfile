ARG JDK_VERSION=17.0.1
FROM openjdk:${JDK_VERSION}-slim AS scheduler

ARG VERSION=0.38.1-alpha

ENV APPLICATION airbyte-scheduler
ENV VERSION ${VERSION}

WORKDIR /app

ADD bin/${APPLICATION}-${VERSION}.tar /app

# wait for upstream dependencies to become available before starting server
ENTRYPOINT ["/bin/bash", "-c", "${APPLICATION}-${VERSION}/bin/${APPLICATION}"]

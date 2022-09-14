ARG JDK_VERSION=17
ARG JDK_IMAGE=eclipse-temurin:${JDK_VERSION}-jdk-jammy
FROM ${JDK_IMAGE} AS metrics-reporter

ARG VERSION=0.40.5

ENV APPLICATION airbyte-metrics-reporter
ENV VERSION ${VERSION}

WORKDIR /app

ADD bin/${APPLICATION}-${VERSION}.tar /app


# wait for upstream dependencies to become available before starting server
ENTRYPOINT ["/bin/bash", "-c", "${APPLICATION}-${VERSION}/bin/${APPLICATION}"]

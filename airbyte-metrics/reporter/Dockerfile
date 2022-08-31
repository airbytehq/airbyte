ARG JDK_VERSION=19-slim-bullseye
ARG JDK_IMAGE=openjdk:${JDK_VERSION}
FROM ${JDK_IMAGE} AS metrics-reporter

ARG VERSION=0.40.3

ENV APPLICATION airbyte-metrics-reporter
ENV VERSION ${VERSION}

WORKDIR /app

ADD bin/${APPLICATION}-${VERSION}.tar /app


# wait for upstream dependencies to become available before starting server
ENTRYPOINT ["/bin/bash", "-c", "${APPLICATION}-${VERSION}/bin/${APPLICATION}"]

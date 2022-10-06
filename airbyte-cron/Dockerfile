ARG JDK_VERSION=3.1
ARG JDK_IMAGE=airbyte/java-datadog-tracer-base:${JDK_VERSION}
FROM ${JDK_IMAGE} AS cron

ARG VERSION=0.40.11

ENV APPLICATION airbyte-cron
ENV VERSION ${VERSION}

WORKDIR /app

# This is automatically unzipped by Docker
ADD bin/${APPLICATION}-${VERSION}.tar /app

# wait for upstream dependencies to become available before starting server
ENTRYPOINT ["/bin/bash", "-c", "${APPLICATION}-${VERSION}/bin/${APPLICATION}"]

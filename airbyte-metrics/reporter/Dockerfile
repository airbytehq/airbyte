ARG JDK_IMAGE=airbyte/java-datadog-tracer-base:3.2
FROM ${JDK_IMAGE} AS metrics-reporter

ARG VERSION=0.40.14

ENV APPLICATION airbyte-metrics-reporter
ENV VERSION ${VERSION}

WORKDIR /app

ADD bin/${APPLICATION}-${VERSION}.tar /app


# wait for upstream dependencies to become available before starting server
ENTRYPOINT ["/bin/bash", "-c", "${APPLICATION}-${VERSION}/bin/${APPLICATION}"]

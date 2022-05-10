ARG JDK_VERSION=17.0.1
FROM openjdk:${JDK_VERSION}-slim AS metrics-reporter

ARG VERSION=0.38.1-alpha

ENV APPLICATION airbyte-metrics-reporter
ENV VERSION ${VERSION}

WORKDIR /app

ADD bin/${APPLICATION}-${VERSION}.tar /app


# wait for upstream dependencies to become available before starting server
ENTRYPOINT ["/bin/bash", "-c", "${APPLICATION}-${VERSION}/bin/${APPLICATION}"]

ARG JDK_VERSION=17.0.1
ARG JDK_IMAGE=openjdk:${JDK_VERSION}-slim
FROM ${JDK_IMAGE} AS metrics-reporter

ARG VERSION=0.39.29-alpha

ENV APPLICATION airbyte-metrics-reporter
ENV VERSION ${VERSION}

WORKDIR /app

ADD bin/${APPLICATION}-${VERSION}.tar /app


# wait for upstream dependencies to become available before starting server
ENTRYPOINT ["/bin/bash", "-c", "${APPLICATION}-${VERSION}/bin/${APPLICATION}"]

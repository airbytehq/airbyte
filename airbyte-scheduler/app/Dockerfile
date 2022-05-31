ARG JDK_VERSION=17.0.1
ARG JDK_IMAGE=openjdk:${JDK_VERSION}-slim
FROM ${JDK_IMAGE} AS scheduler

ARG VERSION=0.39.5-alpha

ENV APPLICATION airbyte-scheduler
ENV VERSION ${VERSION}

WORKDIR /app

ADD bin/${APPLICATION}-${VERSION}.tar /app

# wait for upstream dependencies to become available before starting server
ENTRYPOINT ["/bin/bash", "-c", "${APPLICATION}-${VERSION}/bin/${APPLICATION}"]

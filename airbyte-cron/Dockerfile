ARG JDK_IMAGE=airbyte/airbyte-base-java-image:1.0
FROM ${JDK_IMAGE} AS cron

ARG VERSION=0.40.32

ENV APPLICATION airbyte-cron
ENV VERSION ${VERSION}

WORKDIR /app

# This is automatically unzipped by Docker
ADD bin/${APPLICATION}-${VERSION}.tar /app

# wait for upstream dependencies to become available before starting server
ENTRYPOINT ["/bin/bash", "-c", "${APPLICATION}-${VERSION}/bin/${APPLICATION}"]

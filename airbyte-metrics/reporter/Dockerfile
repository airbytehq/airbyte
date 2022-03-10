ARG JDK_VERSION=17.0.1
FROM openjdk:${JDK_VERSION}-slim AS metrics-reporter

ENV APPLICATION airbyte-metrics-reporter

WORKDIR /app

ADD bin/${APPLICATION}-0.35.49-alpha.tar /app

# wait for upstream dependencies to become available before starting server
ENTRYPOINT ["/bin/bash", "-c", "${APPLICATION}-0.35.49-alpha/bin/${APPLICATION}"]

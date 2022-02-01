ARG JDK_VERSION=17.0.1
FROM openjdk:${JDK_VERSION}-slim AS server

# Server port
EXPOSE 8000

# JMX port
EXPOSE 1099

ENV APPLICATION airbyte-server

WORKDIR /app

ADD bin/${APPLICATION}-0.35.12-alpha.tar /app

# wait for upstream dependencies to become available before starting server
ENTRYPOINT ["/bin/bash", "-c", "${APPLICATION}-0.35.12-alpha/bin/${APPLICATION}"]

ARG JDK_VERSION=14.0.2
FROM openjdk:${JDK_VERSION}-slim AS server

EXPOSE 8000

ENV APPLICATION airbyte-server

RUN groupadd --gid 1000 airbyte && \
    useradd --uid 1000 --gid airbyte airbyte

WORKDIR /app

ADD bin/${APPLICATION}-0.33.5-alpha.tar /app

# Set user to Airbyte, use numeric value for k8s runAsNonRoot PodSecurityPolicy
USER 1000:1000

# wait for upstream dependencies to become available before starting server
ENTRYPOINT ["/bin/bash", "-c", "${APPLICATION}-0.33.5-alpha/bin/${APPLICATION}"]

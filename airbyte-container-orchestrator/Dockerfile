ARG JDK_VERSION=14.0.2
FROM openjdk:${JDK_VERSION}-slim AS sync-attempt

ARG DOCKER_BUILD_ARCH=amd64

# Install Docker to launch orchestrator images. Eventually should be replaced with Docker-java.
# See https://gitter.im/docker-java/docker-java?at=5f3eb87ba8c1780176603f4e for more information on why we are not currently using Docker-java
RUN apt-get update && apt-get install -y \
                          apt-transport-https \
                          ca-certificates \
                          curl \
                          gnupg-agent \
                          software-properties-common
RUN curl -fsSL https://download.docker.com/linux/debian/gpg | apt-key add -
RUN add-apt-repository \
       "deb [arch=${DOCKER_BUILD_ARCH}] https://download.docker.com/linux/debian \
       $(lsb_release -cs) \
       stable"
RUN apt-get update && apt-get install -y docker-ce-cli jq

ENV APPLICATION airbyte-container-orchestrator
ENV AIRBYTE_ENTRYPOINT "/app/${APPLICATION}-0.35.1-alpha/bin/${APPLICATION}"

WORKDIR /app

# Move orchestrator app
ADD bin/${APPLICATION}-0.35.1-alpha.tar /app

# wait for upstream dependencies to become available before starting server
ENTRYPOINT ["/bin/bash", "-c", "/app/${APPLICATION}-0.35.1-alpha/bin/${APPLICATION}"]

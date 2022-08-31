ARG JDK_VERSION=19-slim-bullseye
ARG JDK_IMAGE=openjdk:${JDK_VERSION}
FROM ${JDK_IMAGE} AS worker

ARG DOCKER_BUILD_ARCH=amd64

# Install Docker to launch worker images. Eventually should be replaced with Docker-java.
# See https://gitter.im/docker-java/docker-java?at=5f3eb87ba8c1780176603f4e for more information on why we are not currently using Docker-java
# See https://docs.docker.com/engine/install/debian/ to understand what the following commands are
# doing.
RUN apt-get update && apt-get install -y \
                          ca-certificates \
                          wget \
                          gnupg \
                          lsb-release
RUN mkdir -p /etc/apt/keyrings
RUN wget -O - https://download.docker.com/linux/debian/gpg | gpg --dearmor -o /etc/apt/keyrings/docker.gpg
RUN echo \
      "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/debian \
      $(lsb_release -cs) stable" | tee /etc/apt/sources.list.d/docker.list > /dev/null
RUN apt-get update && apt-get install -y docker-ce-cli jq

# Install kubectl for copying files to kube pods. Eventually should be replaced with a kube java client.
# See https://github.com/airbytehq/airbyte/issues/8643 for more information on why we are using kubectl for copying.
# The following commands were taken from https://kubernetes.io/docs/tasks/tools/install-kubectl-linux/#install-using-native-package-management
RUN wget -O /usr/share/keyrings/kubernetes-archive-keyring.gpg https://packages.cloud.google.com/apt/doc/apt-key.gpg
RUN echo "deb [signed-by=/usr/share/keyrings/kubernetes-archive-keyring.gpg] https://apt.kubernetes.io/ kubernetes-xenial main" | tee /etc/apt/sources.list.d/kubernetes.list
RUN apt-get update && apt-get install -y kubectl

ARG VERSION=0.40.3

ENV APPLICATION airbyte-workers
ENV VERSION ${VERSION}

WORKDIR /app

# Move worker app
ADD bin/${APPLICATION}-${VERSION}.tar /app

# wait for upstream dependencies to become available before starting server
ENTRYPOINT ["/bin/bash", "-c", "${APPLICATION}-${VERSION}/bin/${APPLICATION}"]

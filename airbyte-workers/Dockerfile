ARG JDK_VERSION=17.0.1
FROM openjdk:17.0.1-slim AS worker

ARG DOCKER_BUILD_ARCH=amd64

# Install Docker to launch worker images. Eventually should be replaced with Docker-java.
# See https://gitter.im/docker-java/docker-java?at=5f3eb87ba8c1780176603f4e for more information on why we are not currently using Docker-java
RUN apt-get update && apt-get install -y \
                          apt-transport-https \
                          ca-certificates \
                          curl \
                          gnupg-agent \
                          software-properties-common
RUN curl -fsSL https://download.docker.com/linux/debian/gpg | apt-key add -
RUN arch=$(arch | sed s/aarch64/arm64/ | sed s/x86_64/amd64/) && \
       add-apt-repository \
       "deb [arch=${arch}] https://download.docker.com/linux/debian \
       $(lsb_release -cs) stable"
RUN apt-get update && apt-get install -y docker-ce-cli jq

# Install kubectl for copying files to kube pods. Eventually should be replaced with a kube java client.
# See https://github.com/airbytehq/airbyte/issues/8643 for more information on why we are using kubectl for copying.
# The following commands were taken from https://kubernetes.io/docs/tasks/tools/install-kubectl-linux/#install-using-native-package-management
RUN curl -fsSLo /usr/share/keyrings/kubernetes-archive-keyring.gpg https://packages.cloud.google.com/apt/doc/apt-key.gpg
RUN echo "deb [signed-by=/usr/share/keyrings/kubernetes-archive-keyring.gpg] https://apt.kubernetes.io/ kubernetes-xenial main" | tee /etc/apt/sources.list.d/kubernetes.list
RUN apt-get update && apt-get install -y kubectl

ARG VERSION=0.36.11-alpha

ENV APPLICATION airbyte-workers
ENV VERSION ${VERSION}

WORKDIR /app

# Move worker app
ADD bin/${APPLICATION}-${VERSION}.tar /app

# wait for upstream dependencies to become available before starting server
ENTRYPOINT ["/bin/bash", "-c", "${APPLICATION}-${VERSION}/bin/${APPLICATION}"]

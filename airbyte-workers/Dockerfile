ARG JDK_VERSION=17.0.1
ARG JDK_IMAGE=openjdk:${JDK_VERSION}-slim
FROM ${JDK_IMAGE} AS worker

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
# arch var used to detect architecture of container. Architecture should be spcified to get proper binaries from repo.
RUN arch=$(dpkg --print-architecture) && \
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

ARG VERSION=0.39.29-alpha

ENV APPLICATION airbyte-workers
ENV VERSION ${VERSION}

WORKDIR /app

# Move worker app
ADD bin/${APPLICATION}-${VERSION}.tar /app

# wait for upstream dependencies to become available before starting server
ENTRYPOINT ["/bin/bash", "-c", "${APPLICATION}-${VERSION}/bin/${APPLICATION}"]

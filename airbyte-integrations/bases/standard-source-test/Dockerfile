ARG JDK_VERSION=17.0.4
FROM amazoncorretto:${JDK_VERSION}

ARG DOCKER_BUILD_ARCH=amd64

# Install Docker to launch worker images. Eventually should be replaced with Docker-java.
# See https://gitter.im/docker-java/docker-java?at=5f3eb87ba8c1780176603f4e for more information on why we are not currently using Docker-java
RUN amazon-linux-extras install -y docker
RUN yum install -y openssl jq tar && yum clean all

ENV APPLICATION standard-source-test

WORKDIR /app

COPY entrypoint.sh .
COPY build/distributions/${APPLICATION}*.tar ${APPLICATION}.tar

RUN tar xf ${APPLICATION}.tar --strip-components=1

ENTRYPOINT ["/app/entrypoint.sh"]

LABEL io.airbyte.version=0.1.0
LABEL io.airbyte.name=airbyte/standard-source-test

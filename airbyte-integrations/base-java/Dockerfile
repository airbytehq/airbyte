FROM airbyte/base:dev

### Install Java (start)
# grabbing contents and env variables from https://github.com/docker-library/openjdk/blob/master/Dockerfile-adopt-debian-slim.template
COPY --from=openjdk:14.0.2-slim / /

# Default to UTF-8 file.encoding
ENV LANG C.UTF-8
ENV JAVA_HOME /usr/local/openjdk-14
ENV PATH $JAVA_HOME/bin:$PATH
ENV JAVA_VERSION 14.0.2
### Install Java (end)

WORKDIR /airbyte
ENV APPLICATION base-java

COPY build/distributions/${APPLICATION}*.tar ${APPLICATION}.tar

RUN tar xf ${APPLICATION}.tar --strip-components=1

# airbyte base commands
ENV AIRBYTE_SPEC_CMD "./bin/base-java --spec"
ENV AIRBYTE_CHECK_CMD "./bin/base-java --check"
ENV AIRBYTE_DISCOVER_CMD "./bin/base-java --discover"
ENV AIRBYTE_READ_CMD "./bin/base-java --write"

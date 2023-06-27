### WARNING ###
# The Java connector Dockerfiles will soon be deprecated.
# This Dockerfile is not used to build the connector image we publish to DockerHub.
# The new logic to build the connector image is declared with Dagger here:
# https://github.com/airbytehq/airbyte/blob/master/tools/ci_connector_ops/ci_connector_ops/pipelines/actions/environments.py#L649

# If you need to add a custom logic to build your connector image, you can do it by adding a finalize_build.sh or finalize_build.py script in the connector folder.
# Please reach out to the Connectors Operations team if you have any question.
FROM airbyte/integration-base-java:dev AS build

WORKDIR /airbyte

ENV APPLICATION destination-s3

COPY build/distributions/${APPLICATION}*.tar ${APPLICATION}.tar

RUN tar xf ${APPLICATION}.tar --strip-components=1 && rm -rf ${APPLICATION}.tar

FROM airbyte/integration-base-java:dev

WORKDIR /airbyte

ENV APPLICATION destination-s3

COPY --from=build /airbyte /airbyte
RUN /bin/bash -c 'set -e && \
    ARCH=`uname -m` && \
    if [ "$ARCH" == "x86_64" ] || [ "$ARCH" = "amd64" ]; then \
       echo "$ARCH" && \
       yum install lzop lzo lzo-dev -y; \
    elif [ "$ARCH" == "aarch64" ] || [ "$ARCH" = "arm64" ]; then \
      echo "$ARCH" && \
      yum group install -y "Development Tools"; \
      yum install lzop lzo lzo-dev wget curl unzip zip maven git which -y; \
      wget https://www.oberhumer.com/opensource/lzo/download/lzo-2.10.tar.gz -P /tmp; \
      cd /tmp && tar xvfz lzo-2.10.tar.gz; \
      cd /tmp/lzo-2.10/ && ./configure --enable-shared --prefix /usr/local/lzo-2.10; \
      cd /tmp/lzo-2.10/ && make; \
      cd /tmp/lzo-2.10/ && make install; \
      git clone https://github.com/twitter/hadoop-lzo.git /usr/lib/hadoop/lib/hadoop-lzo/; \
      curl -s "https://get.sdkman.io" | bash; \
      source /root/.sdkman/bin/sdkman-init.sh; \
      sdk install java 8.0.342-librca; \
      sdk use java 8.0.342-librca; \
      cd /usr/lib/hadoop/lib/hadoop-lzo/ && C_INCLUDE_PATH=/usr/local/lzo-2.10/include LIBRARY_PATH=/usr/local/lzo-2.10/lib mvn clean package; \
      find /usr/lib/hadoop/lib/hadoop-lzo/ -name '*libgplcompression*' -exec cp {} /usr/lib/ \; ;\
    else \
       echo "unknown arch" ;\
    fi'

RUN yum clean all
LABEL io.airbyte.version=0.5.0
LABEL io.airbyte.name=airbyte/destination-s3

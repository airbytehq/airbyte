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
    fi'

RUN yum clean all
LABEL io.airbyte.version=0.5.1
LABEL io.airbyte.name=airbyte/destination-s3

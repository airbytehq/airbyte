FROM airbyte/integration-base-java:dev AS build
WORKDIR /airbyte

ENV APPLICATION source-harness

COPY build/distributions/${APPLICATION}*.tar ${APPLICATION}.tar

RUN tar xf ${APPLICATION}.tar --strip-components=1 && rm -rf ${APPLICATION}.tar

FROM airbyte/integration-base-java:dev
ARG TARGETARCH
WORKDIR /airbyte

ENV APPLICATION source-harness
# Kubectl and socat are needed in order to create a pod similar to cloud orchestrator
# It brings up in cluster the source pod to measure, and communicates over socat
RUN curl -O https://s3.us-west-2.amazonaws.com/amazon-eks/1.25.6/2023-01-30/bin/linux/${TARGETARCH}/kubectl
RUN chmod +x ./kubectl
RUN mv ./kubectl /bin/
RUN yum install -y socat && yum clean all

COPY --from=build /airbyte /airbyte
COPY base.sh .

LABEL io.airbyte.version=0.1
LABEL io.airbyte.name=airbyte/source-harness

FROM airbyte/integration-base-java:dev AS build

WORKDIR /airbyte

ENV APPLICATION source-postgres

COPY build/distributions/${APPLICATION}*.tar ${APPLICATION}.tar

# To pretend being a heartbeat monitor. Although somehow this isn't working/isn't getting loaded on the path.
#RUN yum install -y socat
#
#RUN curl -O https://s3.us-west-2.amazonaws.com/amazon-eks/1.21.14/2022-10-31/bin/linux/arm64/kubectl && \
#    chmod +x ./kubectl && \
#    mkdir -p $HOME/bin && cp ./kubectl $HOME/bin/kubectl && export PATH=$PATH:$HOME/bin;

RUN tar xf ${APPLICATION}.tar --strip-components=1 && rm -rf ${APPLICATION}.tar

FROM airbyte/integration-base-java:dev

WORKDIR /airbyte

ENV APPLICATION source-postgres

COPY --from=build /airbyte /airbyte

LABEL io.airbyte.version=1.0.35
LABEL io.airbyte.name=airbyte/source-postgres

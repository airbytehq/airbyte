FROM openjdk:14.0.2-slim

WORKDIR /airbyte

COPY build/distributions/airbyte-workers*.tar airbyte-workers.tar

RUN tar xf airbyte-workers.tar --strip-components=1

ENTRYPOINT ["./bin/airbyte-workers"]

LABEL io.airbyte.version=0.1.0
LABEL io.airbyte.name=airbyte/kube-sync-worker-test

ARG ALPINE_IMAGE=alpine:3.4
FROM ${ALPINE_IMAGE}

RUN apk --no-cache add curl tar \
    && curl -OL https://github.com/danielgtaylor/restish/releases/download/v0.9.0/restish-0.9.0-linux-`uname -m`.tar.gz \
    && tar -C /usr/local/bin -xzf restish-0.9.0-linux-`uname -m`.tar.gz \
    && rm -rf restish-0.9.0-linux-`uname -m`.tar.gz

ENTRYPOINT ["restish"]

LABEL io.airbyte.version=0.1.0
LABEL io.airbyte.name=airbyte/cli

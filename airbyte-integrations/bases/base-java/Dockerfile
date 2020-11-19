FROM openjdk:14.0.2-slim
COPY --from=airbyte/integration-base:dev /airbyte /airbyte
COPY --from=airbyte/normalization:dev /airbyte /airbyte

# Install Python stack
RUN apt-get update \
    && apt-get --yes --no-install-recommends install \
        python3 python3-dev \
        python3-pip python3-venv python3-wheel python3-setuptools \
        build-essential cmake \
        git openssh-client \
        libssl-dev libffi-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /airbyte/base_python_structs
RUN pip3 install .
WORKDIR /airbyte/normalization_code
RUN pip3 install .

WORKDIR /airbyte

COPY javabase.sh .

# airbyte base commands
ENV AIRBYTE_SPEC_CMD "/airbyte/javabase.sh --spec"
ENV AIRBYTE_CHECK_CMD "/airbyte/javabase.sh --check"
ENV AIRBYTE_DISCOVER_CMD "/airbyte/javabase.sh --discover"
ENV AIRBYTE_READ_CMD "/airbyte/javabase.sh --read"
ENV AIRBYTE_WRITE_CMD "/airbyte/javabase.sh --write"

ENTRYPOINT ["/airbyte/base.sh"]

LABEL io.airbyte.version=0.1.0
LABEL io.airbyte.name=airbyte/integration-base-java

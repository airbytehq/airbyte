FROM airbyte/integration-base-singer:0.1.0

# Bash is installed for more convenient debugging. GCC is required by tap-zoom to compile ciso8601.
ENV DEBIAN_FRONTEND noninteractive
RUN apt-get update \
    && apt-get install -y bash \
    && apt-get install -y gcc \
    && rm -rf /var/lib/apt/lists/*

ENV CODE_PATH="source_zoom_singer"
ENV AIRBYTE_IMPL_MODULE="source_zoom_singer"
ENV AIRBYTE_IMPL_PATH="SourceZoomSinger"

LABEL io.airbyte.version=0.2.0
LABEL io.airbyte.name=airbyte/source-zoom-singer

WORKDIR /airbyte/integration_code
COPY $CODE_PATH ./$CODE_PATH
COPY setup.py ./

RUN pip install .

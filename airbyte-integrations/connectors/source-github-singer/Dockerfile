FROM airbyte/integration-base-singer:dev

RUN apt-get update && apt-get install -y \
    bash \
    && rm -rf /var/lib/apt/lists/*

ENV CODE_PATH="source_github_singer"
ENV AIRBYTE_IMPL_MODULE="source_github_singer"
ENV AIRBYTE_IMPL_PATH="SourceGithubSinger"

LABEL io.airbyte.version=0.1.8
LABEL io.airbyte.name=airbyte/source-github-singer

WORKDIR /airbyte/integration_code
COPY $CODE_PATH ./$CODE_PATH
COPY setup.py ./
RUN pip install ".[main]"

WORKDIR /airbyte


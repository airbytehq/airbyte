FROM airbyte/integration-base-singer:0.1.1

RUN apt-get update && apt-get install -y \
    bash \
    && rm -rf /var/lib/apt/lists/*

ENV CODE_PATH="source_github_singer"

WORKDIR /airbyte/integration_code
COPY $CODE_PATH ./$CODE_PATH
COPY setup.py ./
COPY main.py ./

RUN pip install .

ENTRYPOINT ["python", "/airbyte/integration_code/main.py"]

LABEL io.airbyte.version=0.2.7
LABEL io.airbyte.name=airbyte/source-github-singer

WORKDIR /airbyte


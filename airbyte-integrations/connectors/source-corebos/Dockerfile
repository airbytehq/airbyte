<<<<<<< HEAD
FROM airbyte/integration-base-python:0.1.1
=======
FROM airbyte/integration-base-python:dev
>>>>>>> master

# Bash is installed for more convenient debugging.
RUN apt-get update && apt-get install -y bash && rm -rf /var/lib/apt/lists/*

ENV CODE_PATH="source_corebos"
ENV AIRBYTE_IMPL_MODULE="source_corebos"
ENV AIRBYTE_IMPL_PATH="SourceCorebos"

WORKDIR /airbyte/integration_code
COPY $CODE_PATH ./$CODE_PATH
COPY setup.py ./
<<<<<<< HEAD
RUN pip install .

LABEL io.airbyte.version=0.1.1
=======
RUN pip install ".[main]"

LABEL io.airbyte.version=0.1.0
>>>>>>> master
LABEL io.airbyte.name=airbyte/source-corebos

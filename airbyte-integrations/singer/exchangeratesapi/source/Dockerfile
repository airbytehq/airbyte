FROM airbyte/base-singer:dev

RUN apt-get update && apt-get install -y jq

WORKDIR /airbyte/source_implementation

COPY spec.json /airbyte/exchangeratesapi-files/spec.json

COPY source_implementation/__init__.py ./source_implementation/__init__.py
COPY source_implementation/source_implementation.py ./source_implementation/source_implementation.py
COPY setup.py .
RUN pip install .

WORKDIR /airbyte

LABEL io.airbyte.version=0.1.2

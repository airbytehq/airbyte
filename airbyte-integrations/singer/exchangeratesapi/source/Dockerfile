FROM airbyte/base-singer:dev

WORKDIR /singer

ENV VIRTUAL_ENV=/singer/env
RUN python -m venv $VIRTUAL_ENV
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

# Install dependencies:
COPY requirements.txt .
RUN python -m pip install --upgrade pip && \
  pip install -r requirements.txt

RUN apt-get update && apt-get install -y jq

COPY spec.json /airbyte/exchangeratesapi-files

WORKDIR /airbyte/exchangeratesapi
COPY source_implementation.py ./source_implementation/source_implementation.py
COPY setup.py .
RUN pip install .

WORKDIR /singer

LABEL io.airbyte.version=0.1.2

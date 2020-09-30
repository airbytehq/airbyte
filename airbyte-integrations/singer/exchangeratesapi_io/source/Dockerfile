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

COPY entrypoint.sh .
COPY source_implementation.py /airbyte
COPY spec.json /airbyte

LABEL io.airbyte.version=0.1.2

FROM airbyte/base-singer:dev

WORKDIR /singer

ENV VIRTUAL_ENV=/singer/env
RUN python -m venv $VIRTUAL_ENV
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

# Install dependencies:
COPY requirements.txt .
RUN python -m pip install --upgrade pip && \
  pip install -r requirements.txt

COPY entrypoint.sh .
COPY source_implementation.py /airbyte

LABEL io.airbyte.version=0.1.2

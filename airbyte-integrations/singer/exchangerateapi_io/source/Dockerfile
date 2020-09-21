FROM dataline/singer_base:blah

WORKDIR /singer

ENV VIRTUAL_ENV=/singer/env
RUN python -m venv $VIRTUAL_ENV
ENV PATH="$VIRTUAL_ENV/bin:$PATH"
#ENV SINGER_EXECUTABLE=tap-exchangeratesapi migrate to this when contents of entrypoint.sh have been migrated.
ENV SINGER_EXECUTABLE=/singer/entrypoint.sh

RUN apt-get update && apt-get install -y jq bash

# Install dependencies:
COPY requirements.txt .
RUN python -m pip install --upgrade pip && \
  pip install -r requirements.txt

COPY entrypoint.sh .

ENTRYPOINT ["/singer/entrypoint.sh"]

LABEL io.airbyte.version=0.1.2

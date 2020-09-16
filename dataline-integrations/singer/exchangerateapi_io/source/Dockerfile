FROM dataline/integration-singer-base:dev

RUN apk add --no-cache jq bash

# Install dependencies:
COPY requirements.txt .
RUN python -m pip install --upgrade pip && \
  pip install -r requirements.txt

COPY entrypoint.py .

ENTRYPOINT ["python3", "/singer/entrypoint.py"]

LABEL io.dataline.version=0.1.2

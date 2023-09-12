FROM python:3.9-slim

# Bash is installed for more convenient debugging.
RUN apt-get update && apt-get install --no-install-recommends -y bash  && rm -rf /var/lib/apt/lists/*

WORKDIR /airbyte/integration_code
COPY source_facebook_marketing ./source_facebook_marketing
COPY main.py ./
COPY setup.py ./
RUN pip install --no-cache-dir .

ENV AIRBYTE_ENTRYPOINT "python /airbyte/integration_code/main.py"
ENTRYPOINT ["python", "/airbyte/integration_code/main.py"]


LABEL io.airbyte.version=1.1.7
LABEL io.airbyte.name=ngollperrier/data-facebook-marketing

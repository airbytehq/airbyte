FROM python:3.9-slim

# Bash is installed for more convenient debugging.
RUN apt-get update && apt-get install --no-install-recommends -y bash=3.2.57  #&& rm -rf /var/lib/apt/lists/*

WORKDIR /airbyte/integration_code
COPY source_facebook_marketing ./source_facebook_marketing
COPY main.py ./
COPY setup.py ./
RUN pip install --no-cache-dir .

ENV AIRBYTE_ENTRYPOINT "python /airbyte/integration_code/main.py"
ENTRYPOINT ["python", "/airbyte/integration_code/main.py"]


LABEL io.airbyte.version=0.4.0
LABEL io.airbyte.name=ngollperrier/data-facebook-marketing

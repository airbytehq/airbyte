FROM python:3.9-slim

# Bash is installed for more convenient debugging.
RUN apt-get update && apt-get install -y bash curl unzip && rm -rf /var/lib/apt/lists/*

WORKDIR /airbyte/integration_code
COPY source_meli_full ./source_meli_full
COPY main.py ./
COPY setup.py ./

RUN curl -o awscliv2.zip https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip
RUN unzip awscliv2.zip
RUN ./aws/install

RUN pip install .
RUN pip install xmltodict
RUN pip install credstash
RUN pip install google-cloud-secret-manager
RUN pip install --index-url https://meradata:YZHRoMChxmGN4eYXZE28NusiApFXRMs@pypi.merama.link/simple/ merama-core

# ADD configure_aws_credentials.sh ./
# RUN ./bash/configure_aws_credentials.sh.sh

ENV AIRBYTE_ENTRYPOINT "python /airbyte/integration_code/main.py"
ENTRYPOINT ["python", "/airbyte/integration_code/main.py"]

LABEL io.airbyte.version=0.1.3
LABEL io.airbyte.name=airbyte/source-python-http-tutorial

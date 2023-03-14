FROM python:3.9-slim

# Bash is installed for more convenient debugging.
RUN apt-get update && apt-get install -y bash && rm -rf /var/lib/apt/lists/*

WORKDIR /airbyte/integration_code
COPY source_amplitude ./source_amplitude
COPY main.py ./
COPY setup.py ./
RUN pip install .

ENV AIRBYTE_ENTRYPOINT "python /airbyte/integration_code/main.py"
ENTRYPOINT ["python", "/airbyte/integration_code/main.py"]

<<<<<<< HEAD
LABEL io.airbyte.version=0.1.20
=======
LABEL io.airbyte.version=0.1.23
>>>>>>> upstream/master
LABEL io.airbyte.name=airbyte/source-amplitude

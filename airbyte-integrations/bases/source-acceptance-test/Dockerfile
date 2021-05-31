FROM python:3.7-slim
RUN apt-get update && apt-get install -y bash && rm -rf /var/lib/apt/lists/*
ENV CODE_PATH="source_acceptance_test"

WORKDIR /airbyte/source_acceptance_test
COPY $CODE_PATH ./$CODE_PATH
COPY setup.py ./
COPY pytest.ini ./
RUN pip install .

LABEL io.airbyte.version=0.1.2
LABEL io.airbyte.name=airbyte/source-acceptance-test

ENTRYPOINT ["python", "-m", "pytest", "-p", "source_acceptance_test.plugin"]

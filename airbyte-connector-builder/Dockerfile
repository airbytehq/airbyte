FROM python:3.9-slim

# Bash is installed for more convenient debugging.
RUN apt-get update && apt-get install -y bash && rm -rf /var/lib/apt/lists/*

COPY . /connector_builder/

WORKDIR /connector_builder

RUN pip install .

ENTRYPOINT ["python"]
CMD ["connector_builder/entrypoint.py"]
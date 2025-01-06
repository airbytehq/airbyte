FROM airbyte/base-python:3.9

WORKDIR /airbyte/integration_code

COPY setup.py ./
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . ./

RUN chmod +x airbyte_integrations_entrypoint.sh

ENTRYPOINT ["/airbyte/integration_code/airbyte_integrations_entrypoint.sh"]
# TODO

Installieren: libmariadb-dev und python3.10-dev
(oder vielleicht nicht, TODO)

- Venv mit Python 3.10 anlegen
- poetry install --with dev
- airbyte-ci connectors --name=destination-mariadb build
- kind load docker-image airbyte/destination-mariadb:dev -n airbyte-abctl


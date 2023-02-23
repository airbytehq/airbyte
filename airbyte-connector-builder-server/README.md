# Connector builder


## Getting started 

Set up the virtual environment and install dependencies
```bash
python -m venv .venv
source .venv/bin/activate
pip install .
```

Then run the server
```bash
uvicorn connector_builder.entrypoint:app --host 0.0.0.0 --port 8080
```

The server is now reachable on localhost:8080

## Changing the used CDK version

Update the `airbyte-connector-builder-server/CDK_VERSION` file to point to the target version.
This will make sure both this project and the webapp depending on it will stay in sync.

### OpenAPI generation

Run it via Gradle by running this from the Airbyte project root: 
```bash
./gradlew :airbyte-connector-builder-server:generateOpenApiPythonServer
```

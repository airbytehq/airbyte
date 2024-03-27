# Declarative manifest source

This is a generic source that takes the declarative manifest via a key `__injected_declarative_manifest` of its config.

## Execution
This entrypoint is used for connectors created by the connector builder. These connector's spec is defined in their manifest, which is defined in the config's "__injected_declarative_manifest" field. This allows this entrypoint to be used with any connector manifest.

The spec operation is not supported because the config is not known when running a spec.

## Local development

#### Building

When running a connector locally, you will need to make sure that the CDK generated artifacts are built. Run
```bash
# from airbyte-cdk/python
poetry install
poetry run poe build
```

### Locally running the connector

See `pokeapi_config.json` for an example of a config file that can be passed into the connector.

```bash
# from /airbyte-cdk/python/source-declarative-manifest
poetry run python main.py check --config secrets/config.json
poetry run  python main.py discover --config secrets/config.json
poetry run python main.py read --config secrets/config.json --catalog integration_tests/configured_catalog.json
```

### Locally running the connector docker image

#### Build

First, make sure you build the latest Docker image:
```bash
# from airbyte-cdk/python
docker build -t airbyte/source-declarative-manifest:dev .
```

#### Run

Then run any of the connector commands as follows:

```
docker run --rm -v $(pwd)/secrets:/secrets airbyte/source-declarative-manifest:dev check --config /secrets/config.json
docker run --rm -v $(pwd)/secrets:/secrets airbyte/source-declarative-manifest:dev discover --config /secrets/config.json
docker run --rm -v $(pwd)/secrets:/secrets -v $(pwd)/integration_tests:/integration_tests airbyte/source-declarative-manifest:dev read --config /secrets/config.json --catalog /integration_tests/configured_catalog.json
```

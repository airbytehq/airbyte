# Declarative manifest source

This is a generic source that takes the declarative manifest via a key `__injected_declarative_manifest` of its config.

## Execution
This entrypoint is used for connectors created by the connector builder. These connector's spec is defined in their manifest, which is defined in the config's "__injected_declarative_manifest" field. This allows this entrypoint to be used with any connector manifest.

The spec operation is not supported because the config is not known when running a spec.

## Local development


### Locally running the connector

```
python main.py check --config secrets/config.json
python main.py discover --config secrets/config.json
python main.py read --config secrets/config.json --catalog integration_tests/configured_catalog.json
```

### Locally running the connector docker image


#### Build

You can also build the connector with [`airbyte-ci`](https://github.com/airbytehq/airbyte/blob/master/airbyte-ci/connectors/pipelines/README.md). This is typically used in CI and not needed for your development workflow.

```bash
airbyte-ci connectors ---name=source-declarative-manifest build
```

Once built, the docker image name and tag will be `airbyte/source-declarative-manifest:dev`.


#### Run

Then run any of the connector commands as follows:

```
docker run --rm -v $(pwd)/secrets:/secrets airbyte/source-declarative-manifest:dev check --config /secrets/config.json
docker run --rm -v $(pwd)/secrets:/secrets airbyte/source-declarative-manifest:dev discover --config /secrets/config.json
docker run --rm -v $(pwd)/secrets:/secrets -v $(pwd)/integration_tests:/integration_tests airbyte/source-declarative-manifest:dev read --config /secrets/config.json --catalog /integration_tests/configured_catalog.json
```

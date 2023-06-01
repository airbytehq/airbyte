# Connector Builder Backend

This is the backend for requests from the [Connector Builder](https://docs.airbyte.com/connector-development/connector-builder-ui/overview/).

## Local development

### Locally running the Connector Builder backend

```
python main.py read --config path/to/config --catalog path/to/catalog
```

Note:
- Requires the keys `__injected_declarative_manifest` and `__command` in its config, where `__injected_declarative_manifest` is a JSON manifest and `__command` is one of the commands handled by the ConnectorBuilderHandler (`stream_read`, `list_streams`, or `resolve_manifest`), i.e.
```
{
  "config": <normal config>,
  "__injected_declarative_manifest": {...},
  "__command": <"resolve_manifest" | "list_streams" | "test_read">
}
```
*See [ConnectionSpecification](https://docs.airbyte.com/understanding-airbyte/airbyte-protocol/#actor-specification) for details on the `"config"` key if needed.

- When the `__command` is `list_streams` or `resolve_manifest`, the argument to `catalog` should be an empty string.

### Locally running the docker image

#### Build

First, make sure you build the latest Docker image:
```
./gradlew airbyte-cdk:python:airbyteDocker
```

The docker image name and tag, respectively, are the values of the `io.airbyte.name` and `io.airbyte.version` `LABEL`s in the Dockerfile.

#### Run

Then run any of the connector commands as follows:

```
docker run --rm -v $(pwd)/secrets:/secrets airbyte/source-declarative-manifest:dev read --config /secrets/config.json
```

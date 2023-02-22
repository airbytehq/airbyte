# Declarative manifest source

This is a generic source that takes the declarative manifest via a key `__injected_declarative_manifest` of its config.

## Local development

#### Building

You can also build the connector in Gradle. This is typically used in CI and not needed for your development workflow.

To build using Gradle, from the Airbyte repository root, run:

```
./gradlew airbyte-cdk:python:build
```

### Locally running the connector

```
python main.py check --config secrets/config.json
python main.py discover --config secrets/config.json
python main.py read --config secrets/config.json --catalog integration_tests/configured_catalog.json
```

### Locally running the connector docker image

#### Build

First, make sure you build the latest Docker image:
```
./gradlew airbyte-cdk:python:airbyteDocker
```

The docker image name and tag, respectively, are the values of the `io.airbyte.name` and `io.airbyte.version` `LABEL`s in the Dockerfile.

#### Run

Then run any of the connector commands as follows:

```
docker run --rm -v $(pwd)/secrets:/secrets airbyte/source-declarative-manifest:dev check --config /secrets/config.json
docker run --rm -v $(pwd)/secrets:/secrets airbyte/source-declarative-manifest:dev discover --config /secrets/config.json
docker run --rm -v $(pwd)/secrets:/secrets -v $(pwd)/integration_tests:/integration_tests airbyte/source-declarative-manifest:dev read --config /secrets/config.json --catalog /integration_tests/configured_catalog.json
```

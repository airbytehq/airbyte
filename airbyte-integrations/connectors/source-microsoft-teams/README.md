# Microsoft Teams Source 

This is the repository for the Microsoft Teams source connector, written in Python. 
For information about how to use this connector within Airbyte, see [the documentation](https://docs.airbyte.io/integrations/sources/microsoft-teams).

## Local development

### Prerequisites
**To iterate on this connector, make sure to complete this prerequisites section.**

#### Build & Activate Virtual Environment
First, build the module by running the following from the `airbyte` project root directory: 
```
./gradlew :airbyte-integrations:connectors:source-microsoft-teams:build
```

This will generate a virtualenv for this module in `source-microsoft-teams/.venv`. Make sure this venv is active in your
development environment of choice. To activate the venv from the terminal, run:
```
cd airbyte-integrations/connectors/source-microsoft-teams # cd into the connector directory
source .venv/bin/activate
```
If you are in an IDE, follow your IDE's instructions to activate the virtualenv.

#### Create credentials
**If you are a community contributor**, follow the instructions in the [documentation](https://docs.airbyte.io/integrations/sources/microsoft-teams)
to generate the necessary credentials. Then create a file `secrets/config.json` conforming to the `source_microsoft_teams/spec.json` file.
See `sample_files/sample_config.json` for a sample config file.

**If you are an Airbyte core member**, copy the credentials in RPass under the secret name `source-microsoft-teams-integration-test-config`
and place them into `secrets/config.json`.


### Locally running the connector
```
python main_dev.py spec
python main_dev.py check --config secrets/config.json
python main_dev.py discover --config secrets/config.json
python main_dev.py read --config secrets/config.json --catalog sample_files/configured_catalog.json
```

### Unit Tests
To run unit tests locally, from the connector directory run:
```
pytest unit_tests
```

### Locally running the connector docker image
```
# in airbyte root directory
./gradlew :airbyte-integrations:connectors:source-microsoft-teams:airbyteDocker
docker run --rm airbyte/source-microsoft-teams:dev spec
docker run --rm -v $(pwd)/airbyte-integrations/connectors/source-microsoft-teams/secrets:/secrets airbyte/source-microsoft-teams:dev check --config /secrets/config.json
docker run --rm -v $(pwd)/airbyte-integrations/connectors/source-microsoft-teams/secrets:/secrets airbyte/source-microsoft-teams:dev discover --config /secrets/config.json
docker run --rm -v $(pwd)/airbyte-integrations/connectors/source-microsoft-teams/secrets:/secrets -v $(pwd)/airbyte-integrations/connectors/source-microsoft-teams/sample_files:/sample_files airbyte/source-microsoft-teams:dev read --config /secrets/config.json --catalog /sample_files/configured_catalog.json
```

### Integration Tests
1. From the airbyte project root, run `./gradlew :airbyte-integrations:connectors:source-microsoft-teams:standardSourceTestPython` to run the standard integration test suite.
1. To run additional integration tests, place your integration tests in the `integration_tests` directory and run them with `pytest integration_tests`.
   Make sure to familiarize yourself with [pytest test discovery](https://docs.pytest.org/en/latest/goodpractices.html#test-discovery) to know how your test files and methods should be named.

## Dependency Management
All of your dependencies should go in `setup.py`, NOT `requirements.txt`. The requirements file is only used to connect internal Airbyte dependencies in the monorepo for local development.

# Recurly Source 

This is the repository for the Recurly source connector, written in Python. 
For information about how to use this connector within Airbyte, see [the documentation](https://docs.airbyte.io/integrations/sources/recurly).

## Local development
### Build
First, build the module by running the following from the `airbyte` project root directory: 
```
./gradlew :airbyte-integrations:connectors:source-recurly:build
```

This should generate a virtualenv for this module in `source-recurly/.venv`. Make sure this venv is active in your
development environment of choice. If you are on the terminal, run the following from the `source-recurly` directory:
```
cd airbyte-integrations/connectors/source-recurly # cd into the connector directory
source .venv/bin/activate
```
If you are in an IDE, follow your IDE's instructions to activate the virtualenv. 

**All the instructions below assume you have correctly activated the virtualenv.**.

### Locally running the connector
```
python main_dev.py spec
python main_dev.py check --config secrets/config.json
python main_dev.py discover --config secrets/config.json
python main_dev.py read --config secrets/config.json --catalog integration_tests/catalog.json
```

### Unit Tests
To run unit tests locally, from the connector directory run:
```
pytest unit_tests
```

### Locally running the connector docker image
```
# in airbyte root directory
./gradlew :airbyte-integrations:connectors:source-recurly:airbyteDocker
docker run --rm -v $(pwd)/airbyte-integrations/connectors/source-recurly/sample_files:/sample_files airbyte/source-recurly:dev spec
docker run --rm -v $(pwd)/airbyte-integrations/connectors/source-recurly/sample_files:/sample_files airbyte/source-recurly:dev check --config /secrets/config.json
docker run --rm -v $(pwd)/airbyte-integrations/connectors/source-recurly/sample_files:/sample_files airbyte/source-recurly:dev discover --config /secrets/config.json
docker run --rm -v $(pwd)/airbyte-integrations/connectors/source-recurly/sample_files:/sample_files airbyte/source-recurly:dev read --config /secrets/config.json --catalog /integration_tests/catalog.json
```

### Integration Tests 
1. Configure credentials as appropriate, described below.
1. From the airbyte project root, run `./gradlew :airbyte-integrations:connectors:source-recurly:standardSourceTestPython` to run the standard integration test suite.
1. To run additional integration tests, place your integration tests in the `integration_tests` directory and run them with `pytest integration_tests`.
   Make sure to familiarize yourself with [pytest test discovery](https://docs.pytest.org/en/latest/goodpractices.html#test-discovery) to know how your test files and methods should be named.

## Dependency Management
All of your dependencies should go in `setup.py`, NOT `requirements.txt`. The requirements file is only used to connect internal Airbyte dependencies in the monorepo for local development.

## Configure credentials
### Configuring credentials as a community contributor
Follow the instructions in the [documentation](https://docs.airbyte.io/integrations/sources/recurly) to generate credentials, then put those
in `secrets/config.json`.

### Airbyte Employee
Credentials are available in RPass under the secret name `source-recurly-integration-test-creds`.
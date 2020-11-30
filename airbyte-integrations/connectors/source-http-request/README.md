# HTTP Request Source 

This is the repository for the HTTP Request source connector, written in Python. 
For information about how to use this connector within Airbyte, see [the documentation](https://docs.airbyte.io/integrations/sources/rest-api).

## Local development
### Build
First, build the module by running the following from the `airbyte` project root directory: 
```
./gradlew :airbyte-integrations:connectors:source-http-request:build
```

This should generate a virtualenv for this module in `source-http-request/.venv`. Make sure this venv is active in your
development environment of choice. If you are on the terminal, run the following from the `source-http-request` directory:
```
cd airbyte-integrations/connectors/source-http-request # cd into the connector directory
source .venv/bin/activate
```
If you are in an IDE, follow your IDE's instructions to activate the virtualenv. 

**All the instructions below assume you have correctly activated the virtualenv.**.

### Locally running the connector
```
python main_dev.py spec
python main_dev.py check --config sample_files/test_config.json
python main_dev.py discover --config sample_files/test_config.json
python main_dev.py read --config sample_files/test_config.json --catalog sample_files/test_catalog.json
```

### Unit Tests
To run unit tests locally, from the connector directory run:
```
pytest unit_tests
```

### Locally running the connector docker image
```
# in airbyte root directory
./gradlew :airbyte-integrations:connectors:source-http-request:airbyteDocker
docker run --rm -v $(pwd)/airbyte-integrations/connectors/source-http-request:/sample_files airbyte/source-http-request:dev spec
docker run --rm -v $(pwd)/airbyte-integrations/connectors/source-http-request:/sample_files airbyte/source-http-request:dev check --config /sample_files/sample_files/config.json
docker run --rm -v $(pwd)/airbyte-integrations/connectors/source-http-request:/sample_files airbyte/source-http-request:dev discover --config /sample_files/sample_files/config.json
docker run --rm -v $(pwd)/airbyte-integrations/connectors/source-http-request:/sample_files airbyte/source-http-request:dev read --config /sample_files/sample_files/config.json --catalog /sample_files/integration_tests/catalog.json
```

### Integration Tests 
1. Configure credentials as appropriate, described below.
1. From the airbyte project root, run `./gradlew :airbyte-integrations:connectors:source-http-request:standardSourceTestPython` to run the standard integration test suite.
1. To run additional integration tests, place your integration tests in the `integration_tests` directory and run them with `pytest integration_tests`.
   Make sure to familiarize yourself with [pytest test discovery](https://docs.pytest.org/en/latest/goodpractices.html#test-discovery) to know how your test files and methods should be named.

## Dependency Management
All of your dependencies should go in `setup.py`, NOT `requirements.txt`. The requirements file is only used to connect internal Airbyte dependencies in the monorepo for local development.

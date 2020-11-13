# Source Facebook Marketing Api Singer

This is the repository for the Facebook Marketing Api source connector, based on a Singer tap.
For information about how to use this connector within Airbyte, see [the User Documentation](https://docs.airbyte.io/integrations/sources/facebook-marketing-api).

## Local development
### Prerequisites
**To iterate on this connector, make sure to complete this prerequisites section.**

#### Build & Activate Virtual Environment
First, build the module by running the following from the `airbyte` project root directory: 
```
./gradlew :airbyte-integrations:connectors:source-facebook-marketing-api-singer:build
```

This will generate a virtualenv for this module in `source-facebook-marketing-api-singer/.venv`. Make sure this venv is active in your
development environment of choice. If you are on the terminal, run the following
```
cd airbyte-integrations/connectors/source-facebook-marketing-api # cd into the connector directory
source .venv/bin/activate
```
If you are in an IDE, follow your IDE's instructions to activate the virtualenv. 

#### Create credentials
If you are an Airbyte core member, copy the credentials in RPass under the secret name `source-facebook-marketing-api-singer-integration-test-creds`
and place them into `secrets/config.json`.

If you are a contributor, follow the instructions in the [documentation](https://docs.airbyte.io/integrations/sources/facebook-marketing-api) to generate an access token and  obtain your ad account ID. 
Then create a file `secrets/config.json` conforming to the `spec.json` file. See `sample_files/sample_config.json` for a sample config file.

### Locally running the connector
```
python main_dev.py spec
python main_dev.py check --config secrets/config.json
python main_dev.py discover --config secrets/config.json
python main_dev.py read --config secrets/config.json --catalog sample_files/sample_catalog.json
```

### Unit Tests
To run unit tests locally, from the connector root run:
```
pytest unit_tests
```

### Locally running the connector docker image

```
# in airbyte root directory
./gradlew :airbyte-integrations:connectors:source-facebook-marketing-api-singer:airbyteDocker
docker run --rm airbyte/source-facebook-marketing-api-singer:dev spec
docker run --rm -v $(pwd)/airbyte-integrations/connectors/source-facebook-marketing-api-singer/secrets:/secrets airbyte/source-facebook-marketing-api-singer:dev check --config /secrets/config.json
docker run --rm -v $(pwd)/airbyte-integrations/connectors/source-facebook-marketing-api-singer/secrets:/secrets airbyte/source-facebook-marketing-api-singer:dev discover --config /secrets/config.json
docker run --rm -v $(pwd)/airbyte-integrations/connectors/source-facebook-marketing-api-singer/secrets:/secrets -v $(pwd)/airbyte-integrations/connectors/source-facebook-marketing-api-singer/sample_files:/sample_files airbyte/source-facebook-marketing-api-singer:dev read --config /secrets/config.json --catalog /sample_files/sample_catalog.json
```

### Integration Tests 
1. Configure credentials as appropriate, described below.
1. From the airbyte project root, run `./gradlew :airbyte-integrations:connectors:source-facebook-marketing-api-singer:standardSourceTestPython` to run the standard integration test suite.
1. To run additional integration tests, place your integration tests in the `integration_tests` directory and run them with `pytest integration_tests`.
   Make sure to familiarize yourself with [pytest test discovery](https://docs.pytest.org/en/latest/goodpractices.html#test-discovery) to know how your test files and methods should be named.

## Dependency Management
All dependencies should go in `setup.py`, NOT `requirements.txt`. The requirements file is only used to connect internal Airbyte dependencies in the monorepo for local development.

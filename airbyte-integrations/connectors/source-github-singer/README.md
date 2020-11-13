# Source Github Singer

This is the repository for the Github source connector, based on the [tap-github](https://github.com/singer-io/tap-github) Singer tap.

## Local development
### Prerequisites
**To iterate on this connector, make sure to complete this prerequisites section.**

#### Build & Activate Virtual Environment
First, build the module by running the following from the `airbyte` project root directory: 
```
./gradlew :airbyte-integrations:connectors:source-github-singer:build
```

This will generate a virtualenv for this module in `source-github-singer/.venv`. Make sure this venv is active in your
development environment of choice. To activate the venv from the terminal, run:
```
cd airbyte-integrations/connectors/source-github-singer # cd into the connector directory
source .venv/bin/activate
```
If you are in an IDE, follow your IDE's instructions to activate the virtualenv.

#### Create credentials
In order to test the Github source, you will need an access key from github. You can generate one by logging into github and then creating a personal access token [here](https://github.com/settings/tokens).
Then create a file `secrets/config.json` conforming to the `source_github_singer/spec.json` file.

**If you are an Airbyte core member**, copy the credentials in RPass under the secret name `source-github-singer-integration-test-config`
and place them into `secrets/config.json`.

### Locally running the connector
```
python main_dev.py spec
python main_dev.py check --config secrets/config.json
python main_dev.py discover --config secrets/config.json
python main_dev.py read --config secrets/config.json --catalog resourcesstandardtest/catalog.json
```

### Unit Tests
To run unit tests locally, from the connector root run:
```
pytest unit_tests
```

### Locally running the connector docker image
```
# in airbyte root directory
./gradlew :airbyte-integrations:connectors:source-github-singer:airbyteDocker
docker run --rm airbyte/source-github-singer:dev spec
docker run --rm -v $(pwd)/airbyte-integrations/connectors/source-github-singer/secrets:/secrets airbyte/source-github-singer:dev check --config /secrets/config.json
docker run --rm -v $(pwd)/airbyte-integrations/connectors/source-github-singer/secrets:/secrets airbyte/source-github-singer:dev discover --config /secrets/config.json
docker run --rm -v $(pwd)/airbyte-integrations/connectors/source-github-singer/secrets:/secrets -v $(pwd)/airbyte-integrations/connectors/source-github-singer/resourcesstandardtest:/resourcesstandardtest airbyte/source-github-singer:dev read --config /secrets/config.json --catalog /resourcesstandardtest/catalog.json
```

### Integration Tests
1. From the airbyte project root, run `./gradlew :airbyte-integrations:connectors:source-github-singer:standardSourceTestPython` to run the standard integration test suite.
1. To run additional integration tests, place your integration tests in the `integration_tests` directory and run them with `pytest integration_tests`.
   Make sure to familiarize yourself with [pytest test discovery](https://docs.pytest.org/en/latest/goodpractices.html#test-discovery) to know how your test files and methods should be named.

## Dependency Management
All of your dependencies should go in `setup.py`, NOT `requirements.txt`. The requirements file is only used to connect internal Airbyte dependencies in the monorepo for local development.

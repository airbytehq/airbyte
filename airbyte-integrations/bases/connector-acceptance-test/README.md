# Connector Acceptance Tests
This package gathers multiple test suites to assess the sanity of any Airbyte connector.
It is shipped as a [pytest](https://docs.pytest.org/en/7.1.x/) plugin and relies on pytest to discover, configure and execute tests.
Test-specific documentation can be found [here](https://docs.airbyte.com/connector-development/testing-connectors/connector-acceptance-tests-reference/)).

## Running the acceptance tests on a source connector:
1. `cd` into your connector project (e.g. `airbyte-integrations/connectors/source-pokeapi`)
2. Edit `acceptance-test-config.yml` according to your need. Please refer to our [Connector Acceptance Test Reference](https://docs.airbyte.com/connector-development/testing-connectors/connector-acceptance-tests-reference/) if you need details about the available options.
3. Build the connector docker image ( e.g.: `docker build . -t airbyte/source-pokeapi:dev`)
4. Use one of the following ways to run tests (**from your connector project directory**)

### Using `airbyte-ci`
_Note: Install instructions for airbyte-ci are [here](https://github.com/airbytehq/airbyte/blob/master/airbyte-ci/connectors/pipelines/README.md) _

**This runs connector acceptance and other tests that run in our CI**
```bash
airbyte-ci connectors --name=<connector-name> test
```

### Using Bash
```bash
./acceptance-test-docker.sh
```
_Note: this will use the latest docker image for connector-acceptance-test and will also build docker image for the connector_

You can also use the following environment variables with the Gradle and Bash commands:
- `LOCAL_CDK=1`: Run tests against the local python CDK, if relevant. If not set, tests against the latest package published to pypi, or the version specified in the connector's setup.py.
- `FETCH_SECRETS=1`: Fetch secrets required by CATs. This requires you to have a Google Service Account, and the GCP_GSM_CREDENTIALS environment variable to be set, per the instructions [here](https://github.com/airbytehq/airbyte/tree/b03653a24ef16be641333380f3a4d178271df0ee/tools/ci_credentials).

## Running the acceptance tests on multiple connectors:
If you are contributing to the python CDK, you may want to validate your changes by running acceptance tests against multiple connectors.

To do so, from the root of the `airbyte` repo, run `./airbyte-cdk/python/bin/run-cats-with-local-cdk.sh -c <connector1>,<connector2>,...`

## When does acceptance test run?
* When running local acceptance tests on connector:
  * When running `connectorAcceptanceTest` `gradle` task
  * When running or `./acceptance-test-docker.sh` in a connector project
* In the CI on each push to a connector PR.

## Developing on the acceptance tests
You may want to iterate on the acceptance test project itself: adding new tests, fixing a bug etc.
These iterations are more conveniently achieved by remaining in the current directory.

1. `poetry install`
3. Run the unit tests on the acceptance tests themselves: `poetry run python -m pytest unit_tests` (add the `--pdb` option if you want to enable the debugger on test failure)
4. Make the changes you want:
    * Global pytest fixtures are defined in `./connector_acceptance_test/conftest.py`
    * Existing test modules are defined in `./connector_acceptance_test/tests`
    * `acceptance-test-config.yaml` structure is defined in `./connector_acceptance_test/config.py`
5. Unit test your changes by adding tests to `./unit_tests`
6. Run the unit tests on the acceptance tests again: `python -m pytest unit_tests`, make sure the coverage did not decrease. You can bypass slow tests by using the `slow` marker: `python -m pytest unit_tests -m "not slow"`.
7. Manually test the changes you made by running acceptance tests on a specific connector. e.g. `python -m pytest -p connector_acceptance_test.plugin --acceptance-test-config=../../connectors/source-pokeapi`
8. Make sure you updated `docs/connector-development/testing-connectors/connector-acceptance-tests-reference.md` according to your changes
9. Bump the acceptance test docker image version in `airbyte-integrations/bases/connector-acceptance-test/Dockerfile`
10. Update the project changelog `airbyte-integrations/bases/connector-acceptance-test/CHANGELOG.md`
11. Open a PR on our GitHub repository
12. Run the unit test on the CI by running `/legacy-test connector=bases/connector-acceptance-test` in a GitHub comment
13. Publish the new acceptance test version if your PR is approved by running `/legacy-publish connector=bases/connector-acceptance-test` in a GitHub comment
14. Merge your PR

## Migrating `acceptance-test-config.yml` to latest configuration format
We introduced changes in the structure of `acceptance-test-config.yml` files in version 0.2.12.
The *legacy* configuration format is still supported but should be deprecated soon.
To migrate a legacy configuration to the latest configuration format please run:

```bash
python -m venv .venv # If you don't have a virtualenv already
source ./.venv/bin/activate # If you're not in your virtualenv already
python connector_acceptance_test/tools/strictness_level_migration/config_migration.py ../../connectors/source-to-migrate/acceptance-test-config.yml
```

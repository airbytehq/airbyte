# Connector Acceptance Tests
This package gathers multiple test suites to assess the sanity of any Airbyte connector. 
It is shipped as a [pytest](https://docs.pytest.org/en/7.1.x/) plugin and relies on pytest to discover, configure and execute tests.
Test-specific documentation can be found [here](https://docs.airbyte.com/connector-development/testing-connectors/connector-acceptance-tests-reference/)).

## Running the acceptance tests on a source connector:
1. `cd` into your connector project (e.g. `airbyte-integrations/connectors/source-pokeapi`) 
2. Edit `acceptance-test-config.yml` according to your need. Please refer to our [Connector Acceptance Test Reference](https://docs.airbyte.com/connector-development/testing-connectors/connector-acceptance-tests-reference/) if you need details about the available options.
3. Build the connector docker image ( e.g.: `docker build . -t airbyte/source-pokeapi:dev`)
4. Use one of the following ways to run tests (**from your connector project directory**)

**Using python**
```bash
python -m pytest integration_tests -p integration_tests.acceptance
```
_Note: this will assume that docker image for connector is already built_

**Using Gradle**
```bash
./gradlew :airbyte-integrations:connectors:source-<name>:connectorAcceptanceTest
```
_Note: this way will also build docker image for the connector_

**Using Bash**
```bash
./acceptance-test-docker.sh
```
_Note: this will use the latest docker image for connector-acceptance-test and will also build docker image for the connector_

## When does acceptance test run?
* When running local acceptance tests on connector:
  * When running `connectorAcceptanceTest` `gradle` task
  * When running or `./acceptance-test-docker.sh` in a connector project
* When running `/test` command on a GitHub pull request.
* When running `/publish` command on a GitHub pull request.
* When running ` integration-test` GitHub action that is creating the JSON files linked to from [connector builds summary](https://github.com/airbytehq/airbyte/blob/master/airbyte-integrations/builds.md).

## Developing on the acceptance tests
You may want to iterate on the acceptance test project itself: adding new tests, fixing a bug etc.
These iterations are more conveniently achieved by remaining in the current directory.

1. Create a `virtualenv`: `python -m venv .venv`
2. Activate the `virtualenv`: `source ./.venv/bin/activate`
3. Install requirements: `pip install -e .`
4. Run the unit tests on the acceptance tests themselves: `python -m pytest unit_tests` (add the `--pdb` option if you want to enable the debugger on test failure)
5. Make the changes you want:
    * Global pytest fixtures are defined in `./connector_acceptance_test/conftest.py`
    * Existing test modules are defined in `./connector_acceptance_test/tests`
    * `acceptance-test-config.yaml` structure is defined in `./connector_acceptance_test/config.py`
6. Unit test your changes by adding tests to `./unit_tests`
7. Run the unit tests on the acceptance tests again: `python -m pytest unit_tests`, make sure the coverage did not decrease. You can bypass slow tests by using the `slow` marker: `python -m pytest unit_tests -m "not slow"`.
8. Manually test the changes you made by running acceptance tests on a specific connector. e.g. `python -m pytest -p connector_acceptance_test.plugin --acceptance-test-config=../../connectors/source-pokeapi`
9. Make sure you updated `docs/connector-development/testing-connectors/connector-acceptance-tests-reference.md` according to your changes
10. Bump the acceptance test docker image version in `airbyte-integrations/bases/connector-acceptance-test/Dockerfile`
11. Update the project changelog `airbyte-integrations/bases/connector-acceptance-test/CHANGELOG.md`
12. Open a PR on our GitHub repository
13. Run the unit test on the CI by running `/test connector=bases/connector-acceptance-test` in a GitHub comment
14. Publish the new acceptance test version if your PR is approved by running `/publish connector=bases/connector-acceptance-test auto-bump-version=false` in a GitHub comment
15. Merge your PR

## Migrating `acceptance-test-config.yml` to latest configuration format
We introduced changes in the structure of `acceptance-test-config.yml` files in version 0.2.12.
The *legacy* configuration format is still supported but should be deprecated soon.
To migrate a legacy configuration to the latest configuration format please run:

```bash
python -m venv .venv # If you don't have a virtualenv already
source ./.venv/bin/activate # If you're not in your virtualenv already
python connector_acceptance_test/tools/strictness_level_migration/config_migration.py ../../connectors/source-to-migrate/acceptance-test-config.yml
```
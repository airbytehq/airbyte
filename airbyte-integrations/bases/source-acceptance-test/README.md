# Source Acceptance Tests
This package gathers multiple test suites to assess the sanity of any Airbyte **source** connector. 
It is shipped as a [pytest](https://docs.pytest.org/en/7.1.x/) plugin and relies on pytest to discover, configure and execute tests.
Test-specific documentation can be found [here](https://docs.airbyte.com/connector-development/testing-connectors/source-acceptance-tests-reference/)).

## Running the acceptance tests on a source connector:
1. `cd` into your connector project (e.g. `airbyte-integrations/connectors/source-pokeapi`) 
2. Edit `acceptance-test-config.yml` according to your need. Please refer to our [Source Acceptance Test Reference](https://docs.airbyte.com/connector-development/testing-connectors/source-acceptance-tests-reference/) if you need details about the available options.
3. Build the connector docker image ( e.g.: `docker build . -t airbyte/source-pokeapi:dev`)
4. Use one of the following ways to run tests (**from your connector project directory**)

**Using python**
```bash
python -m pytest integration_tests -p integration_tests.acceptance
```
_Note: this will assume that docker image for connector is already built_

**Using Gradle**
```bash
./gradlew :airbyte-integrations:connectors:source-<name>:sourceAcceptanceTest
```
_Note: this way will also build docker image for the connector_

**Using Bash**
```bash
./acceptance-test-docker.sh
```
_Note: this will use the latest docker image for source-acceptance-test and will also build docker image for the connector_

## When does SAT run?
* When running local acceptance tests on connector:
  * When running `sourceAcceptanceTest` `gradle` task
  * When running or `./acceptance-test-docker.sh` in a connector project
* When running `/test` command on a GitHub pull request.
* When running `/publish` command on a GitHub pull request.
* When running ` integration-test` GitHub action that is creating the [connector builds summary](https://github.com/airbytehq/airbyte/blob/master/airbyte-integrations/builds.md).

## Developing on the SAT 
You may want to iterate on the SAT project: adding new tests, fixing a bug etc.
These iterations are more conveniently achieved by remaining in the current directory.

1. Create a `virtualenv`: `python -m venv .venv`
2. Activate the `virtualenv`: `source ./.venv/bin/activate`
3. Install requirements: `pip install -e .`
4. Run the unit tests on SAT: `python -m pytest unit_tests` (add the `--pdb` option if you want to enable the debugger on test failure)
5. Make the changes you want:
    * Global pytest fixtures are defined in `./source_acceptance_test/conftest.py`
    * Existing test modules are defined in `./source_acceptance_test/tests`
    * `acceptance-test-config.yaml` structure is defined in `./source_acceptance_test/config.py`
6. Unit test your changes by adding tests to `./unit_tests`
7. Run the unit tests on SAT again: `python -m pytest unit_tests`, make sure the coverage did not decrease. You can bypass slow tests by using the `slow` marker: `python -m pytest unit_tests -m "not slow"`.
8. Manually test the changes you made by running SAT on a specific connector. e.g. `python -m pytest -p source_acceptance_test.plugin --acceptance-test-config=../../connectors/source-pokeapi`
9. Make sure you updated `docs/connector-development/testing-connectors/source-acceptance-tests-reference.md` according to your changes
10. Bump the SAT version in `airbyte-integrations/bases/source-acceptance-test/Dockerfile`
11. Update the project changelog `airbyte-integrations/bases/source-acceptance-test/CHANGELOG.md`
12. Open a PR on our GitHub repository
13. Run the unit test on the CI by running `/test connector=bases/source-acceptance-test` in a GitHub comment
14. Publish the new SAT version if your PR is approved by running `/publish connector=bases/source-acceptance-test auto-bump-version=false` in a GitHub comment
15. Merge your PR
# Connector Acceptance Tests (CAT)

This package gathers multiple test suites to assess the sanity of any Airbyte connector.
It is shipped as a [pytest](https://docs.pytest.org/en/7.1.x/) plugin and relies on pytest to discover, configure and execute tests.
Test-specific documentation can be found [here](https://docs.airbyte.com/connector-development/testing-connectors/connector-acceptance-tests-reference/).

## Configuration

The acceptance tests are configured via the `acceptance-test-config.yml` YAML file, which is passed to the plugin via the `--acceptance-test-config` option.

## Running the acceptance tests locally

Note there are MANY ways to do this at this time, but we are working on consolidating them.

Which method you choose to use depends on the context you are in.

Pre-requisites:

- Setting up a Service Account for Google Secrets Manager (GSM) access. See [here](https://github.com/airbytehq/airbyte/blob/master/airbyte-ci/connectors/ci_credentials/README.md)
- Ensuring that you have the `GCP_GSM_CREDENTIALS` environment variable set to the contents of your GSM service account key file.
- [Poetry](https://python-poetry.org/docs/#installation) installed
- [Pipx](https://pypa.github.io/pipx/installation/) installed

### Running CAT in the same environment as our CI/CD pipeline (`airbyte-ci`)

_Note: Install instructions for airbyte-ci are [here](https://github.com/airbytehq/airbyte/blob/master/airbyte-ci/connectors/pipelines/README.md) _

**This runs connector acceptance and other tests that run in our CI**

```bash
airbyte-ci connectors --name=<connector-name> test
```

### Running CAT locally for Debugging/Development Purposes

**Pre-requisites:**

To learn how to set up `ci_credentials` and your GSM Service account see [here](https://github.com/airbytehq/airbyte/blob/master/airbyte-ci/connectors/ci_credentials/README.md)

```bash
# Hook up your GSM service account
export GCP_GSM_CREDENTIALS=`cat <path-to-gsm-service-account-key-file>`

# Install the credentials tool
pipx install airbyte-ci/connectors/ci_credentials/ --force --editable
```

**Retrieve a connectors sandbox secrets**

```bash
# From the root of the airbyte repo

# Writes the secrets to airbyte-integrations/connectors/source-faker/secrets
VERSION=dev ci_credentials connectors/source-faker write-to-storage
```

**Run install dependencies**

```bash
# Navigate to our CAT test directory
cd airbyte-integrations/bases/connector-acceptance-test/

# Install dependencies
poetry install
```

**Run the tests**

```bash
# Run tests against your connector
poetry run pytest -p connector_acceptance_test.plugin --acceptance-test-config=../../connectors/source-faker --pdb
```

### Manually

1. `cd` into your connector project (e.g. `airbyte-integrations/connectors/source-pokeapi`)
2. Edit `acceptance-test-config.yml` according to your need. Please refer to our [Connector Acceptance Test Reference](https://docs.airbyte.com/connector-development/testing-connectors/connector-acceptance-tests-reference/) if you need details about the available options.
3. Build the connector docker image ( e.g.: `airbyte-ci connectors --name=source-pokeapi build`)
4. Use one of the following ways to run tests (**from your connector project directory**)

## Developing on the acceptance tests

You may want to iterate on the acceptance test project itself: adding new tests, fixing a bug etc.
These iterations are more conveniently achieved by remaining in the current directory.

1. Install dependencies via `poetry install`
2. Run the unit tests on the acceptance tests themselves: `poetry run pytest unit_tests` (add the `--pdb` option if you want to enable the debugger on test failure)
3. To run specific unit test(s), add `-k` to the above command, e.g. `poetry run python -m pytest unit_tests -k 'test_property_can_store_secret'`. You can use wildcards `*` here as well.
4. Make the changes you want:
   - Global pytest fixtures are defined in `./connector_acceptance_test/conftest.py`
   - Existing test modules are defined in `./connector_acceptance_test/tests`
   - `acceptance-test-config.yaml` structure is defined in `./connector_acceptance_test/config.py`
5. Unit test your changes by adding tests to `./unit_tests`
6. Run the unit tests on the acceptance tests again: `poetry run pytest unit_tests`, make sure the coverage did not decrease. You can bypass slow tests by using the `slow` marker: `poetry run pytest unit_tests -m "not slow"`.
7. Manually test the changes you made by running acceptance tests on a specific connector:
   - First build the connector to ensure your local image is up-to-date: `airbyte-ci connectors --name=source-pokeapi build`
   - Then run the acceptance tests on the connector: `poetry run pytest -p connector_acceptance_test.plugin --acceptance-test-config=../../connectors/source-pokeapi`
8. Make sure you updated `docs/connector-development/testing-connectors/connector-acceptance-tests-reference.md` according to your changes
9. Update the project changelog `airbyte-integrations/bases/connector-acceptance-test/CHANGELOG.md`
10. Open a PR on our GitHub repository
11. This [GitHub action workflow](https://github.com/airbytehq/airbyte/blob/master/.github/workflows/cat-tests.yml) will be triggered and run the unit tests on your branch.
12. Publish the new acceptance test version if your PR is approved by running `/legacy-publish connector=bases/connector-acceptance-test run-tests=false` in a GitHub comment
13. Merge your PR

## Migrating `acceptance-test-config.yml` to latest configuration format

We introduced changes in the structure of `acceptance-test-config.yml` files in version 0.2.12.
The _legacy_ configuration format is still supported but should be deprecated soon.
To migrate a legacy configuration to the latest configuration format please run:

```bash
python -m venv .venv # If you don't have a virtualenv already
source ./.venv/bin/activate # If you're not in your virtualenv already
python connector_acceptance_test/tools/strictness_level_migration/config_migration.py ../../connectors/source-to-migrate/acceptance-test-config.yml
```

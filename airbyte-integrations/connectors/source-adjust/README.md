# Adjust Source

This is the repository for the Adjust source connector, written in Python.
For information about how to use this connector within Airbyte, see [the documentation](https://docs.airbyte.io/integrations/sources/adjust).

## Local development

### Prerequisites
**To iterate on this connector, make sure to complete this prerequisites section.**

#### Minimum Python version required `= 3.9.0`

#### Build & Activate Virtual Environment and install dependencies
From this connector directory, create a virtual environment:
```
python -m venv .venv
```

This will generate a virtualenv for this module in `.venv/`. Make sure this venv is active in your
development environment of choice. To activate it from the terminal, run:
```
source .venv/bin/activate
pip install -r requirements.txt
pip install '.[tests]'
```
If you are in an IDE, follow your IDE's instructions to activate the virtualenv.

Note that while we are installing dependencies from `requirements.txt`, you should only edit `setup.py` for your dependencies. `requirements.txt` is
used for editable installs (`pip install -e`) to pull in Python dependencies from the monorepo and will call `setup.py`.
If this is mumbo jumbo to you, don't worry about it, just put your deps in `setup.py` but install using `pip install -r requirements.txt` and everything
should work as you expect.

#### Create credentials
**If you are a community contributor**, follow the instructions in the [documentation](https://docs.airbyte.io/integrations/sources/adjust)
to generate the necessary credentials. Then create a file `secrets/config.json` conforming to the `source_adjust/spec.yaml` file.
Note that any directory named `secrets` is gitignored across the entire Airbyte repo, so there is no danger of accidentally checking in sensitive information.
See `integration_tests/sample_config.json` for a sample config file.

**If you are an Airbyte core member**, copy the credentials in Lastpass under the secret name `source adjust test creds`
and place them into `secrets/config.json`.

### Locally running the connector
```
python main.py spec
python main.py check --config secrets/config.json
python main.py discover --config secrets/config.json
python main.py read --config secrets/config.json --catalog integration_tests/configured_catalog.json
```

### Locally running the connector docker image


#### Build
**Via [`airbyte-ci`](https://github.com/airbytehq/airbyte/blob/master/airbyte-ci/connectors/pipelines/README.md) (recommended):**
```bash
airbyte-ci connectors --name source-adjust build
```

An image will be built with the tag `airbyte/source-adjust:dev`.

**Via `docker build`:**
```bash
docker build -t airbyte/source-adjust:dev .
```

#### Run
Then run any of the connector commands as follows:
```
docker run --rm airbyte/source-adjust:dev spec
docker run --rm -v $(pwd)/secrets:/secrets airbyte/source-adjust:dev check --config /secrets/config.json
docker run --rm -v $(pwd)/secrets:/secrets airbyte/source-adjust:dev discover --config /secrets/config.json
docker run --rm -v $(pwd)/secrets:/secrets -v $(pwd)/integration_tests:/integration_tests airbyte/source-adjust:dev read --config /secrets/config.json --catalog /integration_tests/configured_catalog.json
```

## Testing
You can run our full test suite locally using [`airbyte-ci`](https://github.com/airbytehq/airbyte/blob/master/airbyte-ci/connectors/pipelines/README.md):
```bash
airbyte-ci connectors --name=source-adjust test
```

### Customizing acceptance Tests
Customize `acceptance-test-config.yml` file to configure tests. See [Connector Acceptance Tests](https://docs.airbyte.com/connector-development/testing-connectors/connector-acceptance-tests-reference) for more information.
If your connector requires to create or destroy resources for use during acceptance tests create fixtures for it and place them inside integration_tests/acceptance.py.

## Dependency Management
All of your dependencies should go in `setup.py`, NOT `requirements.txt`. The requirements file is only used to connect internal Airbyte dependencies in the monorepo for local development.
We split dependencies between two groups, dependencies that are:
* required for your connector to work need to go to `MAIN_REQUIREMENTS` list.
* required for the testing need to go to `TEST_REQUIREMENTS` list

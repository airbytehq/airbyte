# Netsuite Odbc Source

This is the repository for the Netsuite Odbc source connector, written in Python.
For information about how to use this connector within Airbyte, see [the documentation](https://docs.airbyte.com/integrations/sources/netsuite-odbc).

## Local development

### Prerequisites

**To iterate on this connector, make sure to complete this prerequisites section.**

#### Minimum Python version required `= 3.9.0`

#### Activate Virtual Environment and install dependencies

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

**If you are a community contributor**, follow the instructions in the [documentation](https://docs.airbyte.com/integrations/sources/netsuite-odbc)
to generate the necessary credentials. Then create a file `secrets/config.json` conforming to the `source_netsuite_odbc/spec.yaml` file.
Note that any directory named `secrets` is gitignored across the entire Airbyte repo, so there is no danger of accidentally checking in sensitive information.
See `integration_tests/sample_config.json` for a sample config file.

**If you are an Airbyte core member**, copy the credentials in Lastpass under the secret name `source netsuite-odbc test creds`
and place them into `secrets/config.json`.

### Locally running the connector

This connector does not work locally. It must be run through the docker image.
This is because we need to set up the ODBC driver in the docker environment.

### Locally running the connector docker image

#### Use `airbyte-ci` to build your connector

The Airbyte way of building this connector is to use our `airbyte-ci` tool.
You can follow install instructions [here](https://github.com/airbytehq/airbyte/blob/master/airbyte-ci/connectors/pipelines/README.md#L1).
Then running the following command will build your connector:

```bash
airbyte-ci connectors --name source-netsuite-odbc build
```

Once the command is done, you will find your connector image in your local docker registry: `airbyte/source-netsuite-odbc:dev`.

#### Build your own connector image

This connector is built using our dynamic built process in `airbyte-ci`.
The build logic is defined using [Dagger](https://dagger.io/) [here](https://github.com/airbytehq/airbyte/blob/master/airbyte-ci/connectors/pipelines/pipelines/builds/python_connectors.py).

While other connectors rely on the Airbyte Base docker image, this connector defines it's own Dockerfile. If you want to
change the build process, please change the Dockerfile.

2. Build your image:

```bash
docker build -t airbyte/source-netsuite-odbc:dev .
# Running the spec command against your patched connector
docker run airbyte/source-netsuite-odbc:dev spec
```

#### Run

Then run any of the connector commands as follows:

```
docker run --rm airbyte/source-netsuite-odbc:dev spec
docker run --rm -v $(pwd)/secrets:/secrets airbyte/source-netsuite-odbc:dev check --config /secrets/config.json
docker run --rm -v $(pwd)/secrets:/secrets airbyte/source-netsuite-odbc:dev discover --config /secrets/config.json
docker run --rm -v $(pwd)/secrets:/secrets -v $(pwd)/integration_tests:/integration_tests airbyte/source-netsuite-odbc:dev read --config /secrets/config.json --catalog /integration_tests/configured_catalog.json
```

## Testing

Make sure to familiarize yourself with [pytest test discovery](https://docs.pytest.org/en/latest/goodpractices.html#test-discovery) to know how your test files and methods should be named.
First install test dependencies into your virtual environment:

```
pip install .[tests]
```

If on M1, please run the following commands:

```
brew install unixodbc
pip uninstall pyodbc
pip install --pre --no-binary :all: pyodbc
```

### Unit Tests

To run unit tests locally, from the connector directory run:

```
python -m pytest unit_tests
```

### Integration Tests

There are two types of integration tests: Acceptance Tests (Airbyte's test suite for all source connectors) and custom integration tests (which are specific to this connector).

#### Custom Integration tests

Place custom tests inside `integration_tests/` folder, then, from the connector root, run

```
python -m pytest integration_tests
```

#### Acceptance Tests

Customize `acceptance-test-config.yml` file to configure tests. See [Connector Acceptance Tests](https://docs.airbyte.com/connector-development/testing-connectors/connector-acceptance-tests-reference) for more information.
If your connector requires to create or destroy resources for use during acceptance tests create fixtures for it and place them inside integration_tests/acceptance.py.
To run your integration tests with acceptance tests, from the connector root, run

```
python -m pytest integration_tests -p integration_tests.acceptance
```

To run your integration tests with docker

### Using `airbyte-ci` to run tests

See [airbyte-ci documentation](https://github.com/airbytehq/airbyte/blob/master/airbyte-ci/connectors/pipelines/README.md#connectors-test-command)

## Dependency Management

All of your dependencies should go in `setup.py`, NOT `requirements.txt`. The requirements file is only used to connect internal Airbyte dependencies in the monorepo for local development.
We split dependencies between two groups, dependencies that are:

- required for your connector to work need to go to `MAIN_REQUIREMENTS` list.
- required for the testing need to go to `TEST_REQUIREMENTS` list

### Publishing a new version of the connector

You've checked out the repo, implemented a million dollar feature, and you're ready to share your changes with the world. Now what?

1. Make sure your changes are passing unit and integration tests.
1. Bump the connector version in `Dockerfile` -- just increment the value of the `LABEL io.airbyte.version` appropriately (we use [SemVer](https://semver.org/)).
1. Create a Pull Request.
1. Pat yourself on the back for being an awesome contributor.
1. Someone from Airbyte will take a look at your PR and iterate with you to merge it into master.

# SFTP Bulk Source

This is the repository for the FTP source connector, written in Python, that helps you bulk ingest files with the same data format from an FTP server into a single stream.
For information about how to use this connector within Airbyte, see [the documentation](https://docs.airbyte.io/integrations/sources/sftp-bulk).

## Local development

### Prerequisites

**To iterate on this connector, make sure to complete this prerequisites section.**

#### Minimum Python version required `= 3.10.0`

#### Build & Activate Virtual Environment and install dependencies

From this connector directory, create a virtual environment.

```bash
python -m venv .venv
```

This will generate a virtualenv for this module in `.venv/`. Make sure this venv is active in your
development environment of choice. To activate it from the terminal, run:

```bash
source .venv/bin/activate
```

Alternatively, we recommend using `poetry`, install it by following the instructions [here](https://python-poetry.org/docs/#installation). You can configure poetry to create this virtual environment for you by running:

```bash
poetry config virtualenvs.create true
```

You can also configure it so that the virtual environment is created in the project directory at `./.venv` by running:

```bash
poetry config virtualenvs.in-project true
```

With a virtual environment activated, install the dependencies:

```bash
poetry install
```

If you want to install the `connector-acceptance-test` package at the root of the airbyte project, run:

```bash
poetry install --with acceptance-tests
```

If you want to install testing dependencies, run:

```bash
poetry install -E tests
```

If you are in an IDE, follow your IDE's instructions to activate the virtualenv.

#### Building via Gradle

From the Airbyte repository root, run:

```bash
./gradlew :airbyte-integrations:connectors:source-sftp-bulk:build
```

#### Create credentials

**If you are a community contributor**, follow the instructions in the [documentation](https://docs.airbyte.io/integrations/sources/sftp-bulk)
to generate the necessary credentials. Then create a file `secrets/config.json` conforming to the `source_sftp_bulk/spec.json` file.
Note that the `secrets` directory is ignored by git by default, so there is no danger of accidentally checking in sensitive information.
See `integration_tests/sample_config.json` for a sample config file.

**If you are an Airbyte core member**, copy the credentials in Lastpass under the secret name `source ftp test creds`
and place them into `secrets/config.json`.

### Locally running the connector

```bash
python main.py spec
python main.py check --config secrets/config.json
python main.py discover --config secrets/config.json
python main.py read --config secrets/config.json --catalog integration_tests/configured_catalog.json
```

### Locally running the connector docker image

#### Build

First, make sure you build the latest Docker image:

```bash
docker build . -t airbyte/source-sftp-bulk:dev
```

or alternatively `make docker.build_dev`.

You can also build the connector image via Gradle:

```bash
./gradlew :airbyte-integrations:connectors:source-sftp-bulk:airbyteDocker
```

When building via Gradle, the docker image name and tag, respectively, are the values of the `io.airbyte.name` and `io.airbyte.version` `LABEL`s in
the Dockerfile.

#### Run

Then run any of the connector commands as follows:

```bash
docker run --rm airbyte/source-sftp-bulk:dev spec
docker run --rm -v $(pwd)/secrets:/secrets airbyte/source-sftp-bulk:dev check --config /secrets/config.json
docker run --rm -v $(pwd)/secrets:/secrets airbyte/source-sftp-bulk:dev discover --config /secrets/config.json
docker run --rm -v $(pwd)/secrets:/secrets -v $(pwd)/integration_tests:/integration_tests airbyte/source-sftp-bulk:dev read --config /secrets/config.json --catalog /integration_tests/configured_catalog.json
```

## Testing

Make sure to familiarize yourself with [pytest test discovery](https://docs.pytest.org/en/latest/goodpractices.html#test-discovery) to know how your test files and methods should be named.
First install test dependencies into your virtual environment:

```bash
poetry install -E tests
```

or alternatively:

```bash
pip install .[tests]
```

### Unit Tests

To run unit tests locally, from the connector directory run:

```bash
python -m pytest unit_tests
```

### Integration Tests

There are two types of integration tests: Acceptance Tests (Airbyte's test suite for all source connectors) and custom integration tests (which are specific to this connector).

#### Custom Integration tests

Place custom tests inside `integration_tests/` folder, then, from the connector root, run

```bash
python -m pytest integration_tests
```

#### Acceptance Tests

Customize `acceptance-test-config.yml` file to configure tests. See [Connector Acceptance Tests](https://docs.airbyte.io/connector-development/testing-connectors/connector-acceptance-tests-reference) for more information.
If your connector requires to create or destroy resources for use during acceptance tests create fixtures for it and place them inside integration_tests/acceptance.py.
To run your integration tests with acceptance tests, from the connector root, run

```bash
python -m pytest integration_tests -p integration_tests.acceptance
```

To run your integration tests with docker

### Using gradle to run tests

All commands should be run from airbyte project root.
To run unit tests:

```bash
./gradlew :airbyte-integrations:connectors:source-sftp-bulk:unitTest
```

To run acceptance and custom integration tests:

```bash
./gradlew :airbyte-integrations:connectors:source-sftp-bulk:integrationTest
```

## Dependency Management

This connector uses [Poetry](https://python-poetry.org/) for dependency management. To add a new dependency, run:

```bash
poetry add <package-name> [--optional]
```

Make a dependency optional by passing `--optional`. Add a dependency to an optional group (e.g. `tests`) by editing `pyproject.toml`.

### Publishing a new version of the connector

You've checked out the repo, implemented a million dollar feature, and you're ready to share your changes with the world. Now what?

1. Make sure your changes are passing unit and integration tests.
2. Bump the connector version in `Dockerfile` -- just increment the value of the `LABEL io.airbyte.version` appropriately (we use [SemVer](https://semver.org/)).
3. Bump the package version at `pyproject.toml`
4. Create a Pull Request.
5. Pat yourself on the back for being an awesome contributor.
6. Someone from Airbyte will take a look at your PR and iterate with you to merge it into master.

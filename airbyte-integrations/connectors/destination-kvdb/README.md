# Kvdb Destination

This is the repository for the [Kvdb](https://kvdb.io) destination connector, written in Python. It is intended to be an example for how to write a Python destination. KvDB is a very simple key value store, which makes it great for the purposes of illustrating how to write a Python destination connector.

## Local development

### Prerequisites

**To iterate on this connector, make sure to complete this prerequisites section.**

#### Minimum Python version required `= 3.7.0`

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
```

If you are in an IDE, follow your IDE's instructions to activate the virtualenv.

Note that while we are installing dependencies from `requirements.txt`, you should only edit `setup.py` for your dependencies. `requirements.txt` is
used for editable installs (`pip install -e`) to pull in Python dependencies from the monorepo and will call `setup.py`.
If this is mumbo jumbo to you, don't worry about it, just put your deps in `setup.py` but install using `pip install -r requirements.txt` and everything
should work as you expect.

#### Building via Gradle

From the Airbyte repository root, run:

```
./gradlew :airbyte-integrations:connectors:destination-kvdb:build
```

#### Create credentials

**If you are a community contributor**, generate the necessary credentials from [Kvdb](https://kvdb.io/docs/api/), and then create a file `secrets/config.json` conforming to the `destination_kvdb/spec.json` file.
Note that the `secrets` directory is gitignored by default, so there is no danger of accidentally checking in sensitive information.
See `integration_tests/sample_config.json` for a sample config file.

**If you are an Airbyte core member**, copy the credentials in Lastpass under the secret name `destination kvdb test creds`
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
airbyte-ci connectors --name=destination-kvdb build
```

An image will be built with the tag `airbyte/destination-kvdb:dev`.

**Via `docker build`:**

```bash
docker build -t airbyte/destination-kvdb:dev .
```

#### Run

Then run any of the connector commands as follows:

```
docker run --rm airbyte/destination-kvdb:dev spec
docker run --rm -v $(pwd)/secrets:/secrets airbyte/destination-kvdb:dev check --config /secrets/config.json
# messages.jsonl is a file containing line-separated JSON representing AirbyteMessages
cat messages.jsonl | docker run --rm -v $(pwd)/secrets:/secrets -v $(pwd)/integration_tests:/integration_tests airbyte/destination-kvdb:dev write --config /secrets/config.json --catalog /integration_tests/configured_catalog.json
```

## Testing

Make sure to familiarize yourself with [pytest test discovery](https://docs.pytest.org/en/latest/goodpractices.html#test-discovery) to know how your test files and methods should be named.
First install test dependencies into your virtual environment:

```
pip install .[tests]
```

### Unit Tests

To run unit tests locally, from the connector directory run:

```
python -m pytest unit_tests
```

### Integration Tests

There are two types of integration tests: Acceptance Tests (Airbyte's test suite for all destination connectors) and custom integration tests (which are specific to this connector).

#### Custom Integration tests

Place custom tests inside `integration_tests/` folder, then, from the connector root, run

```
python -m pytest integration_tests
```

#### Acceptance Tests

You can run our full test suite locally using [`airbyte-ci`](https://github.com/airbytehq/airbyte/blob/master/airbyte-ci/connectors/pipelines/README.md):

```bash
airbyte-ci connectors --name=destination-kvdb test
```

## Dependency Management

All of your dependencies should go in `setup.py`, NOT `requirements.txt`. The requirements file is only used to connect internal Airbyte dependencies in the monorepo for local development.
We split dependencies between two groups, dependencies that are:

- required for your connector to work need to go to `MAIN_REQUIREMENTS` list.
- required for the testing need to go to `TEST_REQUIREMENTS` list

### Publishing a new version of the connector

You've checked out the repo, implemented a million dollar feature, and you're ready to share your changes with the world. Now what?

1. Make sure your changes are passing our test suite: `airbyte-ci connectors --name=destination-kvdb test`
2. Bump the connector version in `metadata.yaml`: increment the `dockerImageTag` value. Please follow [semantic versioning for connectors](https://docs.airbyte.com/contributing-to-airbyte/resources/pull-requests-handbook/#semantic-versioning-for-connectors).
3. Make sure the `metadata.yaml` content is up to date.
4. Make the connector documentation and its changelog is up to date (`docs/integrations/destinations/kvdb.md`).
5. Create a Pull Request: use [our PR naming conventions](https://docs.airbyte.com/contributing-to-airbyte/resources/pull-requests-handbook/#pull-request-title-convention).
6. Pat yourself on the back for being an awesome contributor.
7. Someone from Airbyte will take a look at your PR and iterate with you to merge it into master.

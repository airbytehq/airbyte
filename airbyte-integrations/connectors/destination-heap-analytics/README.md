# Heap Analytics Destination

This is the repository for the Heap Analytics destination connector, written in Python.
For information about how to use this connector within Airbyte, see [the documentation](https://docs.airbyte.io/integrations/destinations/heap-analytics).

## Local development

### Prerequisites
**To iterate on this connector, make sure to complete this prerequisites section.**

#### Minimum Python version required `= 3.7.0`

#### Build & Activate Virtual Environment and install dependencies

From this connector directory, create a virtualenv:
```
python -m venv .venv
```

This will generate a virtual environment for this module in `.venv/`. Make sure this venv is active in your
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
./gradlew :airbyte-integrations:connectors:destination-heap-analytics:build
```

#### Create credentials
**If you are a community contributor**, follow the instructions in the [documentation](https://docs.airbyte.io/integrations/destinations/heap-analytics)
to generate the necessary credentials. Then create a file `secrets/config.json` conforming to the `destination_heap_analytics/spec.json` file.
Note that the `secrets` directory is gitignored by default, so there is no danger of accidentally checking in sensitive information.
See `integration_tests/sample_config.json` for a sample config file.

**If you are an Airbyte core member**, copy the app id in Lastpass under the secret name `destination heap-analytics app id` and replace the app_id under the `sample_files/config-*.json`

### Locally running the connector

#### Server-Side API - Track

Use [this API](https://developers.heap.io/reference/track-1) to send custom events to Heap server-side.

```bash
python main.py spec
python main.py check --config sample_files/config-events.json
cat sample_files/messages.jsonl | python main.py write --config sample_files/config-events.json --catalog sample_files/configured_catalog.json
```

#### Server-Side API - Add User Properties

[This API](https://developers.heap.io/reference/add-user-properties) allows you to attach custom properties to any identified users from your servers, such as Sign Up Date (in ISO8601 format), Total # Transactions Completed, or Total Dollars Spent.

```bash
python main.py spec
python main.py check --config sample_files/config-aup.json
cat sample_files/messages.jsonl | python main.py write --config sample_files/config-aup.json --catalog sample_files/configured_catalog.json
```

#### Server-Side API - Add Account Properties

[This API](https://developers.heap.io/reference/add-account-properties) allows you to attach custom account properties to users. An account ID or use of our Salesforce integration is required for this to work.

```bash
python main.py spec
python main.py check --config sample_files/config-aap.json
cat sample_files/messages.jsonl | python main.py write --config sample_files/config-aap.json --catalog sample_files/configured_catalog.json
```

### Locally running the connector docker image

#### Build

First, make sure you build the latest Docker image:

```bash
docker build . -t airbyte/destination-heap-analytics:dev
```

You can also build the connector image via Gradle:

```bash
./gradlew :airbyte-integrations:connectors:destination-heap-analytics:airbyteDocker
```

When building via Gradle, the docker image name and tag, respectively, are the values of the `io.airbyte.name` and `io.airbyte.version` `LABEL`s in
the Dockerfile.

#### Run

Then run any of the connector commands as follows:
Spec command

```bash
docker run --rm airbyte/destination-heap-analytics:dev spec
```

Check command

```bash
docker run --rm -v $(pwd)/sample_files:/sample_files airbyte/destination-heap-analytics:dev check --config /sample_files/config-events.json
docker run --rm -v $(pwd)/sample_files:/sample_files airbyte/destination-heap-analytics:dev check --config /sample_files/config-aap.json
docker run --rm -v $(pwd)/sample_files:/sample_files airbyte/destination-heap-analytics:dev check --config /sample_files/config-aup.json
```

Write command
```bash
# messages.jsonl is a file containing line-separated JSON representing AirbyteMessages
cat sample_files/messages.jsonl | docker run --rm -v $(pwd)/sample_files:/sample_files airbyte/destination-heap-analytics:dev write --config /sample_files/config-events.json --catalog /sample_files/configured_catalog.json
cat sample_files/messages.jsonl | docker run --rm -v $(pwd)/sample_files:/sample_files airbyte/destination-heap-analytics:dev write --config /sample_files/config-aup.json --catalog /sample_files/configured_catalog.json
cat sample_files/messages.jsonl | docker run --rm -v $(pwd)/sample_files:/sample_files airbyte/destination-heap-analytics:dev write --config /sample_files/config-aap.json --catalog /sample_files/configured_catalog.json
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

```bash
python -m pytest integration_tests
```

### Using gradle to run tests

All commands should be run from airbyte project root.
To run unit tests:

```bash
./gradlew :airbyte-integrations:connectors:destination-heap-analytics:unitTest
```

To run acceptance and custom integration tests:
```bash
./gradlew :airbyte-integrations:connectors:destination-heap-analytics:integrationTest
```

## Dependency Management

All of your dependencies should go in `setup.py`, NOT `requirements.txt`. The requirements file is only used to connect internal Airbyte dependencies in the monorepo for local development.
We split dependencies between two groups, dependencies that are:

* required for your connector to work need to go to `MAIN_REQUIREMENTS` list.
* required for the testing need to go to `TEST_REQUIREMENTS` list

### Publishing a new version of the connector

You've checked out the repo, implemented a million dollar feature, and you're ready to share your changes with the world. Now what?
1. Make sure your changes are passing unit and integration tests.
2. Bump the connector version in `Dockerfile` -- just increment the value of the `LABEL io.airbyte.version` appropriately (we use [SemVer](https://semver.org/)).
3. Create a Pull Request.
4. Pat yourself on the back for being an awesome contributor.
5. Someone from Airbyte will take a look at your PR and iterate with you to merge it into master.

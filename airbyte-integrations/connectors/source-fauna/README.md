# New Readers

If you know how Airbyte works, read [bootstrap.md](bootstrap.md) for a quick introduction to this source. If you haven't
used airbyte before, read [overview.md](overview.md) for a longer overview about what this connector is and how to use
it.

# For Fauna Developers

## Running locally

First, start a local fauna container:
```
docker run --rm --name faunadb -p 8443:8443 fauna/faunadb
```

In another terminal, cd into the connector directory:
```
cd airbyte-integrations/connectors/source-fauna
```

Once started the container is up, setup the database:
```
fauna eval "$(cat examples/setup_database.fql)" --domain localhost --port 8443 --scheme http --secret secret
```

Finally, run the connector:
```
python main.py spec
python main.py check --config examples/config_localhost.json
python main.py discover --config examples/config_localhost.json
python main.py read --config examples/config_localhost.json --catalog examples/configured_catalog.json
```

To pick up a partial failure you need to pass in a state file. To test via example induce a crash via bad data (e.g. a missing required field), update `examples/sample_state_full_sync.json` to contain your emitted state and then run:

```
python main.py read --config examples/config_localhost.json --catalog examples/configured_catalog.json --state examples/sample_state_full_sync.json
```

## Running the intergration tests

First, cd into the connector directory:
```
cd airbyte-integrations/connectors/source-fauna
```

The integration tests require a secret config.json. Ping me on slack to get this file.
Once you have this file, put it in `secrets/config.json`. A sample of this file can be
found at `examples/secret_config.json`. Once the file is created, build the connector:
```
docker build . -t airbyte/source-fauna:dev
```

Now, run the integration tests:
```
python -m pytest -p integration_tests.acceptance
```


# Fauna Source

This is the repository for the Fauna source connector, written in Python.
For information about how to use this connector within Airbyte, see [the documentation](https://docs.airbyte.io/integrations/sources/fauna).

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
```
If you are in an IDE, follow your IDE's instructions to activate the virtualenv.

Note that while we are installing dependencies from `requirements.txt`, you should only edit `setup.py` for your dependencies. `requirements.txt` is
used for editable installs (`pip install -e`) to pull in Python dependencies from the monorepo and will call `setup.py`.
If this is mumbo jumbo to you, don't worry about it, just put your deps in `setup.py` but install using `pip install -r requirements.txt` and everything
should work as you expect.

#### Building via Gradle
From the Airbyte repository root, run:
```
./gradlew :airbyte-integrations:connectors:source-fauna:build
```

#### Create credentials
**If you are a community contributor**, follow the instructions in the [documentation](https://docs.airbyte.io/integrations/sources/fauna)
to generate the necessary credentials. Then create a file `secrets/config.json` conforming to the `source_fauna/spec.yaml` file.
Note that the `secrets` directory is gitignored by default, so there is no danger of accidentally checking in sensitive information.
See `examples/secret_config.json` for a sample config file.

**If you are an Airbyte core member**, copy the credentials in Lastpass under the secret name `source fauna test creds`
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
First, make sure you build the latest Docker image:
```
docker build . -t airbyte/source-fauna:dev
```

You can also build the connector image via Gradle:
```
./gradlew :airbyte-integrations:connectors:source-fauna:airbyteDocker
```
When building via Gradle, the docker image name and tag, respectively, are the values of the `io.airbyte.name` and `io.airbyte.version` `LABEL`s in
the Dockerfile.

#### Run
Then run any of the connector commands as follows:
```
docker run --rm airbyte/source-fauna:dev spec
docker run --rm -v $(pwd)/secrets:/secrets airbyte/source-fauna:dev check --config /secrets/config.json
docker run --rm -v $(pwd)/secrets:/secrets airbyte/source-fauna:dev discover --config /secrets/config.json
docker run --rm -v $(pwd)/secrets:/secrets -v $(pwd)/integration_tests:/integration_tests airbyte/source-fauna:dev read --config /secrets/config.json --catalog /integration_tests/configured_catalog.json
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
There are two types of integration tests: Acceptance Tests (Airbyte's test suite for all source connectors) and custom integration tests (which are specific to this connector).
#### Custom Integration tests
Place custom tests inside `integration_tests/` folder, then, from the connector root, run
```
python -m pytest integration_tests
```
#### Acceptance Tests
Customize `acceptance-test-config.yml` file to configure tests. See [Source Acceptance Tests](https://docs.airbyte.io/connector-development/testing-connectors/source-acceptance-tests-reference) for more information.
If your connector requires to create or destroy resources for use during acceptance tests create fixtures for it and place them inside integration_tests/acceptance.py.
To run your integration tests with acceptance tests, from the connector root, run
```
python -m pytest integration_tests -p integration_tests.acceptance
```
To run your integration tests with docker

### Using gradle to run tests
All commands should be run from airbyte project root.
To run unit tests:
```
./gradlew :airbyte-integrations:connectors:source-fauna:unitTest
```
To run acceptance and custom integration tests:
```
./gradlew :airbyte-integrations:connectors:source-fauna:integrationTest
```

## Dependency Management
All of your dependencies should go in `setup.py`, NOT `requirements.txt`. The requirements file is only used to connect internal Airbyte dependencies in the monorepo for local development.
We split dependencies between two groups, dependencies that are:
* required for your connector to work need to go to `MAIN_REQUIREMENTS` list.
* required for the testing need to go to `TEST_REQUIREMENTS` list

### Publishing a new version of the connector
You've checked out the repo, implemented a million dollar feature, and you're ready to share your changes with the world. Now what?
1. Make sure your changes are passing unit and integration tests.
1. Bump the connector version in `Dockerfile` -- just increment the value of the `LABEL io.airbyte.version` appropriately (we use [SemVer](https://semver.org/)).
1. Create a Pull Request.
1. Pat yourself on the back for being an awesome contributor.
1. Someone from Airbyte will take a look at your PR and iterate with you to merge it into master.

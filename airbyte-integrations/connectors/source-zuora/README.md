# Zuora Source

This is the repository for the Zuora source connector, written in Python.
For information about how to use this connector within Airbyte, see [the documentation](https://docs.airbyte.io/integrations/sources/zuora).

## Local development

### Prerequisites
**To iterate on this connector, make sure to complete this prerequisites section.**

#### Minimum Python version required `= 3.7.0`

#### Build & Activate Virtual Environment and install dependencies
From this connector directory, create a virtual environment:
```
python3 -m venv .venv
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
You can also build the connector in Gradle. This is typically used in CI and not needed for your development workflow.

To build using Gradle, from the Airbyte repository root, run:
```
./gradlew :airbyte-integrations:connectors:source-zuora:build
```

#### Create credentials
**If you are a community contributor**, follow the instructions in the [documentation](https://docs.airbyte.io/integrations/sources/zuora)
to generate the necessary credentials. Then create a file `secrets/config.json` conforming to the `source_zuora/spec.json` file.
Note that any directory named `secrets` is gitignored across the entire Airbyte repo, so there is no danger of accidentally checking in sensitive information.
See `integration_tests/sample_config.json` for a sample config file.

**If you are an Airbyte core member**, copy the credentials in Lastpass under the secret name `source zuora test creds`
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
docker build --no-cache .  -t airbyte/source-zuora:dev
```

You can also build the connector image via Gradle:
```
./gradlew clean :airbyte-integrations:connectors:source-zuora:airbyteDocker
```

When building via Gradle, the docker image name and tag, respectively, are the values of the `io.airbyte.name` and `io.airbyte.version` `LABEL`s in
the Dockerfile.

#### Run
Then run any of the connector commands as follows:
```
docker run --rm airbyte/source-zuora:dev spec
docker run --rm -v $(pwd)/secrets:/secrets airbyte/source-zuora:dev check --config /secrets/config.json
docker run --rm -v $(pwd)/secrets:/secrets airbyte/source-zuora:dev discover --config /secrets/config.json
docker run --rm -v $(pwd)/secrets:/secrets -v $(pwd)/integration_tests:/integration_tests airbyte/source-zuora:dev read --config /secrets/config.json --catalog /integration_tests/configured_catalog.json
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
Customize `acceptance-test-config.yml` file to configure tests. See [Connector Acceptance Tests](https://docs.airbyte.io/connector-development/testing-connectors/connector-acceptance-tests-reference) for more information.
If your connector requires to create or destroy resources for use during acceptance tests create fixtures for it and place them inside integration_tests/acceptance.py.
To run your integration tests with acceptance tests, from the connector root, run
```
docker build . --no-cache -t airbyte/source-zuora:dev \
&& python -m pytest -p connector_acceptance_test.plugin
```

To run your integration tests with docker

### Using gradle to run tests
All commands should be run from airbyte project root.
To run unit tests:
```
./gradlew :airbyte-integrations:connectors:source-zuora:unitTest
```

To run acceptance and custom integration tests:
```
./gradlew clean :airbyte-integrations:connectors:source-zuora:integrationTest
```

### Run the actual test using with DBT Normalisation in action
## Add the Zuora Connector you just built:

# Run Airbyte using docker-compose
Under Airbyte's root directory:
```
docker compose up -d
```
Open the web-page of Airbyte:
```
http://localhost:8000/
```
Proceed the `First-Steps` on the web-page, use some test information for this, for now you can skipp the `onboarding` part.

# Add New Source Connector
Add the SOURCE by going to `Admin` panel and press:
```
+ New Connector
```
Complete the New Connector's form by entering:
```
Name : Test Zuora Connector
Image: airbyte/source-zuora
Tag: dev
Documentation: http://SomeTestDocumentation.com/
```
Save the form.

# Add Destination
Use the following steps to build and test the custom destination on the Postgres example:
```
docker run --rm --name airbyte-destination -e POSTGRES_PASSWORD=password -p 3000:5432 -d postgres
```
After the docker has run the local postgres database in the background for your needs, use the following credentials to set up the DESTINATION on the Airbyte's web-page, on your local  machine.
```
Host: localhost
Port: 3000
User: postgres
Password: password
DB Name: postgres
```

# Run the Connection Sync


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

# Jira Source 

This is the repository for the Jira source connector, written in Python. 
For information about how to use this connector within Airbyte, see [the documentation](https://docs.airbyte.io/integrations/sources/jira).

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
./gradlew :airbyte-integrations:connectors:source-jira:build
```

#### Create credentials
**If you are a community contributor**, follow the instructions in the [documentation](https://docs.airbyte.io/integrations/sources/jira)
to generate the necessary credentials. Then create a file `secrets/config.json` conforming to the `source_jira/spec.json` file.
Note that the `secrets` directory is gitignored by default, so there is no danger of accidentally checking in sensitive information.
See `integration_tests/sample_config.json` for a sample config file.

**If you are an Airbyte core member**, copy the credentials in Lastpass under the secret name `source jira test creds`
and place them into `secrets/config.json`.


### Locally running the connector
```
python main.py spec
python main.py check --config secrets/config.json
python main.py discover --config secrets/config.json
python main.py read --config secrets/config.json --catalog integration_tests/configured_catalog.json
```

### Unit Tests
To run unit tests locally, from the connector directory run:
```
python -m pytest unit_tests
```

### Locally running the connector docker image



#### Use `airbyte-ci` to build your connector
The Airbyte way of building this connector is to use our `airbyte-ci` tool.
You can follow install instructions [here](https://github.com/airbytehq/airbyte/blob/master/airbyte-ci/connectors/pipelines/README.md#L1).
Then running the following command will build your connector:

```bash
airbyte-ci connectors --name source-jira build
```
Once the command is done, you will find your connector image in your local docker registry: `airbyte/source-jira:dev`.

##### Customizing our build process
When contributing on our connector you might need to customize the build process to add a system dependency or set an env var.
You can customize our build process by adding a `build_customization.py` module to your connector.
This module should contain a `pre_connector_install` and `post_connector_install` async function that will mutate the base image and the connector container respectively.
It will be imported at runtime by our build process and the functions will be called if they exist.

Here is an example of a `build_customization.py` module:
```python
from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    # Feel free to check the dagger documentation for more information on the Container object and its methods.
    # https://dagger-io.readthedocs.io/en/sdk-python-v0.6.4/
    from dagger import Container


async def pre_connector_install(base_image_container: Container) -> Container:
    return await base_image_container.with_env_variable("MY_PRE_BUILD_ENV_VAR", "my_pre_build_env_var_value")

async def post_connector_install(connector_container: Container) -> Container:
    return await connector_container.with_env_variable("MY_POST_BUILD_ENV_VAR", "my_post_build_env_var_value")
```

#### Build your own connector image
This connector is built using our dynamic built process in `airbyte-ci`.
The base image used to build it is defined within the metadata.yaml file under the `connectorBuildOptions`.
The build logic is defined using [Dagger](https://dagger.io/) [here](https://github.com/airbytehq/airbyte/blob/master/airbyte-ci/connectors/pipelines/pipelines/builds/python_connectors.py).
It does not rely on a Dockerfile.

If you would like to patch our connector and build your own a simple approach would be to:

1. Create your own Dockerfile based on the latest version of the connector image.
```Dockerfile
FROM airbyte/source-jira:latest

COPY . ./airbyte/integration_code
RUN pip install ./airbyte/integration_code

# The entrypoint and default env vars are already set in the base image
# ENV AIRBYTE_ENTRYPOINT "python /airbyte/integration_code/main.py"
# ENTRYPOINT ["python", "/airbyte/integration_code/main.py"]
```
Please use this as an example. This is not optimized.

2. Build your image:
```bash
docker build -t airbyte/source-jira:dev .
# Running the spec command against your patched connector
docker run airbyte/source-jira:dev spec
```
#### Run
Then run any of the connector commands as follows:
```
docker run --rm airbyte/source-jira:dev spec
docker run --rm -v $(pwd)/secrets:/secrets airbyte/source-jira:dev check --config /secrets/config.json
docker run --rm -v $(pwd)/secrets:/secrets airbyte/source-jira:dev discover --config /secrets/config.json
docker run --rm -v $(pwd)/secrets:/secrets -v $(pwd)/integration_tests:/integration_tests airbyte/source-jira:dev read --config /secrets/config.json --catalog /integration_tests/configured_catalog.json
```

#### Acceptance Tests
Customize `acceptance-test-config.yml` file to configure tests. See [Connector Acceptance Tests](https://docs.airbyte.io/connector-development/testing-connectors/connector-acceptance-tests-reference) for more information.
If your connector requires to create or destroy resources for use during acceptance tests create fixtures for it and place them inside integration_tests/acceptance.py.
To run your integration tests with acceptance tests, from the connector root, run
```
docker build . --no-cache -t airbyte/source-jira:dev \
&& python -m pytest -p connector_acceptance_test.plugin
```

### Integration Tests
1. From the airbyte project root, run `./gradlew :airbyte-integrations:connectors:source-jira:integrationTest` to run the standard integration test suite.
1. To run additional integration tests, place your integration tests in a new directory `integration_tests` and run them with `python -m pytest -s integration_tests`.
   Make sure to familiarize yourself with [pytest test discovery](https://docs.pytest.org/en/latest/goodpractices.html#test-discovery) to know how your test files and methods should be named.

## Dependency Management
All of your dependencies should go in `setup.py`, NOT `requirements.txt`. The requirements file is only used to connect internal Airbyte dependencies in the monorepo for local development.

### Publishing a new version of the connector
You've checked out the repo, implemented a million dollar feature, and you're ready to share your changes with the world. Now what?
1. Make sure your changes are passing unit and integration tests
1. Bump the connector version in `Dockerfile` -- just increment the value of the `LABEL io.airbyte.version` appropriately (we use SemVer).
1. Create a Pull Request
1. Pat yourself on the back for being an awesome contributor
1. Someone from Airbyte will take a look at your PR and iterate with you to merge it into master
# PGVector Destination

This is the repository for the PGVector destination connector, written in Python.
For information about how to use this connector within Airbyte, see [the documentation](https://docs.airbyte.com/integrations/destinations/pgvector).

## Local development

### Prerequisites
**To iterate on this connector, make sure to complete this prerequisites section.**

#### Minimum Python version required `= 3.9.0`

### Installing the connector
From this connector directory, run:
```bash
poetry install --with dev.
```

#### Create credentials
**If you are a community contributor**, follow the instructions in the [documentation](https://docs.airbyte.com/integrations/destinations/pgvector)
to generate the necessary credentials. Then create a file `secrets/config.json` conforming to the `destination_pgvector/spec.json` file.
Note that the `secrets` directory is gitignored by default, so there is no danger of accidentally checking in sensitive information.
See `integration_tests/sample_config.json` for a sample config file.

**If you are an Airbyte core member**, copy the credentials in Lastpass under the secret name `destination pgvector test creds`
and place them into `secrets/config.json`.

### Locally running the connector
```
poetry run python main.py spec
poetry run python main.py check --config secrets/config.json
cat examples/messages.jsonl | poetry run python main.py write --config secrets/config.json --catalog examples/configured_catalog.json
```

### Locally running the connector docker image

#### Use `airbyte-ci` to build your connector
The Airbyte way of building this connector is to use our `airbyte-ci` tool.
You can follow install instructions [here](https://github.com/airbytehq/airbyte/blob/master/airbyte-ci/connectors/pipelines/README.md#L1).
Then running the following command will build your connector:

```bash
airbyte-ci connectors --name destination-pgvector build
```
Once the command is done, you will find your connector image in your local docker registry: `airbyte/destination-pgvector:dev`.

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
FROM airbyte/destination-pgvector:latest

COPY . ./airbyte/integration_code
RUN pip install ./airbyte/integration_code

# The entrypoint and default env vars are already set in the base image
# ENV AIRBYTE_ENTRYPOINT "python /airbyte/integration_code/main.py"
# ENTRYPOINT ["python", "/airbyte/integration_code/main.py"]
```
Please use this as an example. This is not optimized.

2. Build your image:
```bash
docker build -t airbyte/destination-pgvector:dev .
# Running the spec command against your patched connector
docker run airbyte/destination-pgvector:dev spec
```
#### Run
Then run any of the connector commands as follows:
```
docker run --rm airbyte/destination-pgvector:dev spec
docker run --rm -v $(pwd)/secrets:/secrets airbyte/destination-pgvector:dev check --config /secrets/config.json
# messages.jsonl is a file containing line-separated JSON representing AirbyteMessages
cat messages.jsonl | docker run --rm -v $(pwd)/secrets:/secrets -v $(pwd)/integration_tests:/integration_tests airbyte/destination-pgvector:dev write --config /secrets/config.json --catalog /integration_tests/configured_catalog.json
```
## Testing
You can run our full test suite locally using [`airbyte-ci`](https://github.com/airbytehq/airbyte/blob/master/airbyte-ci/connectors/pipelines/README.md):
```bash
airbyte-ci connectors --name=destination-pgvector test
```

### Unit Tests
To run unit tests locally, from the connector directory run:
```
poetry run pytest -s unit_tests
```

### Integration Tests
There are two types of integration tests: Acceptance Tests (Airbyte's test suite for all destination connectors) and custom integration tests (which are specific to this connector).

To run integration tests locally, make sure you have a secrets/config.json as explained above, and then run:
```
poetry run pytest -s integration_tests
``` 

### Customizing acceptance Tests
Customize `acceptance-test-config.yml` file to configure tests. See [Connector Acceptance Tests](https://docs.airbyte.com/connector-development/testing-connectors/connector-acceptance-tests-reference) for more information.
If your connector requires to create or destroy resources for use during acceptance tests create fixtures for it and place them inside integration_tests/acceptance.py.

### Using `airbyte-ci` to run tests
See [airbyte-ci documentation](https://github.com/airbytehq/airbyte/blob/master/airbyte-ci/connectors/pipelines/README.md#connectors-test-command)

## Dependency Management
All of your dependencies should go in `pyproject.toml`
* required for your connector to work need to go to `[tool.poetry.dependencies]` list.
* required for the testing need to go to `[tool.poetry.group.dev.dependencies]` list

### Publishing a new version of the connector
You've checked out the repo, implemented a million dollar feature, and you're ready to share your changes with the world. Now what?
1. Make sure your changes are passing unit and integration tests.
1. Bump the connector version in `Dockerfile` -- just increment the value of the `LABEL io.airbyte.version` appropriately (we use [SemVer](https://semver.org/)).
1. Create a Pull Request.
1. Pat yourself on the back for being an awesome contributor.
1. Someone from Airbyte will take a look at your PR and iterate with you to merge it into master.

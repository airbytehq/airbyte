# Migration Guide: How to make a python connector use our base image

We currently enforce our certified python connectors to use our [base image](https://hub.docker.com/r/airbyte/python-connector-base).
This guide will help connector developers to migrate their connector to use our base image.

N.B: This guide currently only applies to Python CDK connectors.

## Prerequisite

[Install the airbyte-ci tool](https://github.com/airbytehq/airbyte/blob/master/airbyte-ci/connectors/pipelines/README.md#L1)

## Definition of a successful migration

1. The connector `Dockerfile` is removed from the connector folder
2. The connector `metadata.yaml` is referencing the latest base image in the `data.connectorBuildOptions.baseImage` key
3. The connector version is bumped by a patch increment
4. A changelog entry is added to the connector documentation file
5. The connector is successfully built and tested by our CI
6. If you add `build_customization.py` to your connector, the Connector Operations team has reviewed and approved your changes.

## Semi automated migration

- Run `airbyte-ci connectors --name=<my-connector> migrate_to_base_image <PR_NUMBER>`
- Commit and push the changes on your PR

## Manual migration

In order for a connector to use our base image it has to declare it in its `metadata.yaml` file under the `data.connectorBuildOptions.baseImage` key:

Example:

```yaml
connectorBuildOptions:
  baseImage: docker.io/airbyte/python-connector-base:1.1.0@sha256:bd98f6505c6764b1b5f99d3aedc23dfc9e9af631a62533f60eb32b1d3dbab20c
```

### Why are we using long addresses instead of tags?

**For build reproducibility!**.
Using full image address allows us to have a more deterministic build process.
If we used tags our connector could get built with a different base image if the tag was overwritten.
In other word, using the image digest (sha256), we have the guarantee that a build, on the same commit, will always use the same base image.

### What if my connector needs specific system dependencies?

Declaring the base image in the metadata.yaml file makes the Dockerfile obselete and the connector will be built using our internal build process declared [here](https://github.com/airbytehq/airbyte/blob/master/airbyte-ci/connectors/pipelines/pipelines/airbyte_ci/connectors/build_image/steps/python_connectors.py#L55).
If your connector has specific system dependencies, or has to set environment variables, we have a pre/post build hook framework for that.

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

### Listing migrated / non migrated connectors:

To list all migrated certified connectors you can ran:

```bash
airbyte-ci connectors --support-level=certified --metadata-query="data.connectorBuildOptions.baseImage is not None" list
```

To list all non migrated certified connectors you can ran:

```bash
airbyte-ci connectors --metadata-query="data.supportLevel == 'certified' and 'connectorBuildOptions' not in data.keys()" list
```

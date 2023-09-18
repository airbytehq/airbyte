# Sentry

This page contains the setup guide and reference information for the Sentry source connector.

## Prerequisites

To set up the Sentry source connector, you'll need the Sentry [project name](https://docs.sentry.io/product/projects/), [authentication token](https://docs.sentry.io/api/auth/#auth-tokens), and [organization](https://docs.sentry.io/product/accounts/membership/).

## Set up the Sentry connector in Airbyte

1. [Log into your Airbyte Cloud](https://cloud.airbyte.com/workspaces) account or navigate to the Airbyte Open Source dashboard.
2. Click **Sources** and then click **+ New source**.
3. On the Set up the source page, select **Sentry** from the Source type dropdown.
4. Enter the name for the Sentry connector.
5. For **Project**, enter the name of the [Sentry project](https://docs.sentry.io/product/projects/) you want to sync.
6. For **Host Name**, enter the host name of your self-hosted Sentry API Server. If your server isn't self-hosted, leave the field blank.
7. For **Authentication Tokens**, enter the [Sentry authentication token](https://docs.sentry.io/api/auth/#auth-tokens).
8. For **Organization**, enter the [Sentry Organization](https://docs.sentry.io/product/accounts/membership/) the groups belong to.
9. Click **Set up source**.

## Supported sync modes

The Sentry source connector supports the following [sync modes](https://docs.airbyte.com/cloud/core-concepts#connection-sync-modes):

- [Full Refresh - Overwrite](https://docs.airbyte.com/understanding-airbyte/connections/full-refresh-overwrite/)
- [Full Refresh - Append](https://docs.airbyte.com/understanding-airbyte/connections/full-refresh-append)
- [Incremental - Append](https://docs.airbyte.com/understanding-airbyte/connections/incremental-append)
- [Incremental - Append + Deduped](https://docs.airbyte.com/understanding-airbyte/connections/incremental-append-deduped)

## Supported Streams

- [Events](https://docs.sentry.io/api/events/list-a-projects-events/)
- [Issues](https://docs.sentry.io/api/events/list-a-projects-issues/)
- [Projects](https://docs.sentry.io/api/projects/list-your-projects/)
- [Releases](https://docs.sentry.io/api/releases/list-an-organizations-releases/)

## Data type map

| Integration Type    | Airbyte Type |
| :------------------ | :----------- |
| `string`            | `string`     |
| `integer`, `number` | `number`     |
| `array`             | `array`      |
| `object`            | `object`     |


## Build instructions
### Build your own connector image
This connector is built using our dynamic built process.
The base image used to build it is defined within the metadata.yaml file under the `connectorBuildOptions`.
The build logic is defined using [Dagger](https://dagger.io/) [here](https://github.com/airbytehq/airbyte/blob/master/airbyte-ci/connectors/pipelines/pipelines/builds/python_connectors.py).
It does not rely on a Dockerfile.

If you would like to patch our connector and build your own a simple approach would be:

1. Create your own Dockerfile based on the latest version of the connector image.
```Dockerfile
FROM airbyte/source-sentry:latest

COPY . ./airbyte/integration_code
RUN pip install ./airbyte/integration_code

# The entrypoint and default env vars are already set in the base image
# ENV AIRBYTE_ENTRYPOINT "python /airbyte/integration_code/main.py"
# ENTRYPOINT ["python", "/airbyte/integration_code/main.py"]
```
Please use this as an example. This is not optimized.

2. Build your image:
```bash
docker build -t airbyte/source-sentry:dev .
# Running the spec command against your patched connector
docker run airbyte/source-sentry:dev spec
```

### Customizing our build process
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
## Changelog

| Version | Date       | Pull Request                                             | Subject                                                                 |
|:--------|:-----------|:---------------------------------------------------------|:------------------------------------------------------------------------|
| 0.3.0 | 2023-09-18 | [30528](https://github.com/airbytehq/airbyte/pull/30528) | Use our base image and remove Dockerfile |
| 0.2.4   | 2023-08-14 | [29401](https://github.com/airbytehq/airbyte/pull/29401) | Fix `null` value in stream state                                        |
| 0.2.3   | 2023-08-03 | [29023](https://github.com/airbytehq/airbyte/pull/29023) | Add incremental for `issues` stream                                     |
| 0.2.2   | 2023-05-02 | [25759](https://github.com/airbytehq/airbyte/pull/25759) | Change stream that used in check_connection                             |
| 0.2.1   | 2023-04-27 | [25602](https://github.com/airbytehq/airbyte/pull/25602) | Add validation of project and organization names during connector setup |
| 0.2.0   | 2023-04-03 | [23923](https://github.com/airbytehq/airbyte/pull/23923) | Add Releases stream                                                     |
| 0.1.12  | 2023-03-01 | [23619](https://github.com/airbytehq/airbyte/pull/23619) | Fix bug when `stream state` is `None` or any other bad value occurs     |
| 0.1.11  | 2023-02-02 | [22303](https://github.com/airbytehq/airbyte/pull/22303) | Turn ON default AvailabilityStrategy                                    |
| 0.1.10  | 2023-01-27 | [22041](https://github.com/airbytehq/airbyte/pull/22041) | Set `AvailabilityStrategy` for streams explicitly to `None`             |
| 0.1.9   | 2022-12-20 | [21864](https://github.com/airbytehq/airbyte/pull/21864) | Add state persistence to incremental sync                               |
| 0.1.8   | 2022-12-20 | [20709](https://github.com/airbytehq/airbyte/pull/20709) | Add incremental sync                                                    |
| 0.1.7   | 2022-09-30 | [17466](https://github.com/airbytehq/airbyte/pull/17466) | Migrate to per-stream states                                            |
| 0.1.6   | 2022-08-29 | [16112](https://github.com/airbytehq/airbyte/pull/16112) | Revert back to the Python CDK                                           |
| 0.1.5   | 2022-08-24 | [15911](https://github.com/airbytehq/airbyte/pull/15911) | Bugfix to allowing reading schemas at runtime                           |
| 0.1.4   | 2022-08-19 | [15800](https://github.com/airbytehq/airbyte/pull/15800) | Bugfix to allow reading sentry.yaml at runtime                          |
| 0.1.3   | 2022-08-17 | [15734](https://github.com/airbytehq/airbyte/pull/15734) | Fix yaml based on the new schema validator                              |
| 0.1.2   | 2021-12-28 | [15345](https://github.com/airbytehq/airbyte/pull/15345) | Migrate to config-based framework                                       |
| 0.1.1   | 2021-12-28 | [8628](https://github.com/airbytehq/airbyte/pull/8628)   | Update fields in source-connectors specifications                       |
| 0.1.0   | 2021-10-12 | [6975](https://github.com/airbytehq/airbyte/pull/6975)   | New Source: Sentry                                                      |
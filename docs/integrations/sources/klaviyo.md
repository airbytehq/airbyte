# Klaviyo

This page contains the setup guide and reference information for the Klaviyo source connector.

## Prerequisites

To set up the Klaviyo source connector, you'll need the [Klaviyo Private API key](https://help.klaviyo.com/hc/en-us/articles/115005062267-How-to-Manage-Your-Account-s-API-Keys#your-private-api-keys3).

## Set up the Klaviyo connector in Airbyte

1. [Log into your Airbyte Cloud](https://cloud.airbyte.com/workspaces) or navigate to the Airbyte Open Source dashboard.
2. Click **Sources** and then click **+ New source**.
3. On the Set up the source page, select **Klaviyo** from the Source type dropdown.
4. Enter the name for the Klaviyo connector.
5. For **Api Key**, enter the Klaviyo [Private API key](https://help.klaviyo.com/hc/en-us/articles/115005062267-How-to-Manage-Your-Account-s-API-Keys#your-private-api-keys3).
6. For **Start Date**, enter the date in YYYY-MM-DD format. The data added on and after this date will be replicated.
7. Click **Set up source**.

## Supported sync modes

The Klaviyo source connector supports the following [sync modes](https://docs.airbyte.com/cloud/core-concepts#connection-sync-modes):

- [Full Refresh - Overwrite](https://docs.airbyte.com/understanding-airbyte/connections/full-refresh-overwrite/)
- [Full Refresh - Append](https://docs.airbyte.com/understanding-airbyte/connections/full-refresh-append)
- [Incremental - Append](https://docs.airbyte.com/understanding-airbyte/connections/incremental-append)
- [Incremental - Append + Deduped](https://docs.airbyte.com/understanding-airbyte/connections/incremental-append-deduped)

## Supported Streams

- [Campaigns](https://developers.klaviyo.com/en/v1-2/reference/get-campaigns#get-campaigns)
- [Events](https://developers.klaviyo.com/en/v1-2/reference/metrics-timeline)
- [GlobalExclusions](https://developers.klaviyo.com/en/v1-2/reference/get-global-exclusions)
- [Lists](https://developers.klaviyo.com/en/v1-2/reference/get-lists)
- [Metrics](https://developers.klaviyo.com/en/v1-2/reference/get-metrics)
- [Flows](https://developers.klaviyo.com/en/reference/get_flows)
- [Profiles](https://developers.klaviyo.com/en/reference/get_profiles)

## Performance considerations

The connector is restricted by Klaviyo [requests limitation](https://apidocs.klaviyo.com/reference/api-overview#rate-limits).

The Klaviyo connector should not run into Klaviyo API limitations under normal usage. [Create an issue](https://github.com/airbytehq/airbyte/issues) if you encounter any rate limit issues that are not automatically retried successfully.

## Data type map

| Integration Type | Airbyte Type | Notes |
| :--------------- | :----------- | :---- |
| `string`         | `string`     |       |
| `number`         | `number`     |       |
| `array`          | `array`      |       |
| `object`         | `object`     |       |


## Build instructions
### Build your own connector image
This connector is built using our dynamic built process.
The base image used to build it is defined within the metadata.yaml file under the `connectorBuildOptions`.
The build logic is defined using [Dagger](https://dagger.io/) [here](https://github.com/airbytehq/airbyte/blob/master/airbyte-ci/connectors/pipelines/pipelines/builds/python_connectors.py).
It does not rely on a Dockerfile.

If you would like to patch our connector and build your own a simple approach would be:

1. Create your own Dockerfile based on the latest version of the connector image.
```Dockerfile
FROM airbyte/source-klaviyo:latest

COPY . ./airbyte/integration_code
RUN pip install ./airbyte/integration_code

# The entrypoint and default env vars are already set in the base image
# ENV AIRBYTE_ENTRYPOINT "python /airbyte/integration_code/main.py"
# ENTRYPOINT ["python", "/airbyte/integration_code/main.py"]
```
Please use this as an example. This is not optimized.

2. Build your image:
```bash
docker build -t airbyte/source-klaviyo:dev .
# Running the spec command against your patched connector
docker run airbyte/source-klaviyo:dev spec
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

| Version  | Date       | Pull Request                                               | Subject                                                                                   |
| :------- | :--------- | :--------------------------------------------------------- | :---------------------------------------------------------------------------------------- |
| 0.4.0 | 2023-09-18 | [30528](https://github.com/airbytehq/airbyte/pull/30528) | Use our base image and remove Dockerfile |
| `0.3.2`  | 2023-06-20 | [27498](https://github.com/airbytehq/airbyte/pull/27498)   | Do not store state in the future                                                          |
| `0.3.1`  | 2023-06-08 | [27162](https://github.com/airbytehq/airbyte/pull/27162)   | Anonymize check connection error message                                                  |
| `0.3.0`  | 2023-02-18 | [23236](https://github.com/airbytehq/airbyte/pull/23236)   | Add ` Email Templates` stream                                                             |
| `0.2.0`  | 2023-03-13 | [22942](https://github.com/airbytehq/airbyte/pull/23968)   | Add `Profiles` stream                                                                     |
| `0.1.13` | 2023-02-13 | [22942](https://github.com/airbytehq/airbyte/pull/22942)   | Specified date formatting in specification                                                |
| `0.1.12` | 2023-01-30 | [22071](https://github.com/airbytehq/airbyte/pull/22071)   | Fix `Events` stream schema                                                                |
| `0.1.11` | 2023-01-27 | [22012](https://github.com/airbytehq/airbyte/pull/22012)   | Set `AvailabilityStrategy` for streams explicitly to `None`                               |
| `0.1.10` | 2022-09-29 | [17422](https://github.com/airbytehq/airbyte/issues/17422) | Update CDK dependency                                                                     |
| `0.1.9`  | 2022-09-28 | [17304](https://github.com/airbytehq/airbyte/issues/17304) | Migrate to per-stream state.                                                              |
| `0.1.6`  | 2022-07-20 | [14872](https://github.com/airbytehq/airbyte/issues/14872) | Increase test coverage                                                                    |
| `0.1.5`  | 2022-07-12 | [14617](https://github.com/airbytehq/airbyte/issues/14617) | Set max_retries = 10 for `lists` stream.                                                  |
| `0.1.4`  | 2022-04-15 | [11723](https://github.com/airbytehq/airbyte/issues/11723) | Enhance klaviyo source for flows stream and update to events stream.                      |
| `0.1.3`  | 2021-12-09 | [8592](https://github.com/airbytehq/airbyte/pull/8592)     | Improve performance, make Global Exclusions stream incremental and enable Metrics stream. |
| `0.1.2`  | 2021-10-19 | [6952](https://github.com/airbytehq/airbyte/pull/6952)     | Update schema validation in SAT                                                           |
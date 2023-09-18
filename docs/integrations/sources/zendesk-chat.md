# Zendesk Chat

This page contains the setup guide and reference information for the Zendesk Chat source connector.

## Prerequisites

- A Zendesk Account with permission to access data from accounts you want to sync.
<!-- env:oss -->
- (Airbyte Open Source) An Access Token (https://developer.zendesk.com/rest_api/docs/chat/auth). We recommend creating a restricted, read-only key specifically for Airbyte access to allow you to control which resources Airbyte should be able to access.
<!-- /env:oss -->

## Setup guide

<!-- env:cloud -->

**For Airbyte Cloud:**

1. [Log into your Airbyte Cloud](https://cloud.airbyte.com/workspaces) account.
2. Click **Sources** and then click **+ New source**.
3. On the Set up the source page, select **Zendesk Chat** from the Source type dropdown.
4. Enter the name for the Zendesk Chat connector.
5. If you access Zendesk Chat from a [Zendesk subdomain](https://support.zendesk.com/hc/en-us/articles/4409381383578-Where-can-I-find-my-Zendesk-subdomain-), enter the **Subdomain**.
6. For **Start Date**, enter the date in `YYYY-MM-DDTHH:mm:ssZ` format. The data added on and after this date will be replicated.
7. Click **Authenticate your Zendesk Chat account**. Log in and authorize your Zendesk Chat account.
8. Click **Set up source**.
<!-- /env:cloud -->

<!-- env:oss -->

**For Airbyte Open Source:**

1. Navigate to the Airbyte Open Source dashboard.
2. Click **Sources** and then click **+ New source**.
3. On the Set up the source page, select **Zendesk Chat** from the Source type dropdown.
4. Enter the name for the Zendesk Chat connector.
5. If you access Zendesk Chat from a [Zendesk subdomain](https://support.zendesk.com/hc/en-us/articles/4409381383578-Where-can-I-find-my-Zendesk-subdomain-), enter the **Subdomain**.
6. For **Start Date**, enter the date in `YYYY-MM-DDTHH:mm:ssZ` format. The data added on and after this date will be replicated.
7. For Authorization Method, select **Access Token** from the dropdown and enter your Zendesk [access token](https://developer.zendesk.com/rest_api/docs/chat/auth).
8. Click **Set up source**.
<!-- /env:oss -->

## Supported sync modes

The Zendesk Chat source connector supports the following [sync modes](https://docs.airbyte.com/cloud/core-concepts#connection-sync-modes):

- [Full Refresh - Overwrite](https://docs.airbyte.com/understanding-airbyte/connections/full-refresh-overwrite/)
- [Full Refresh - Append](https://docs.airbyte.com/understanding-airbyte/connections/full-refresh-append)
- [Incremental - Append](https://docs.airbyte.com/understanding-airbyte/connections/incremental-append)
- [Incremental - Append + Deduped](https://docs.airbyte.com/understanding-airbyte/connections/incremental-append-deduped)

## Supported Streams

- [Accounts](https://developer.zendesk.com/rest_api/docs/chat/accounts#show-account)
- [Agents](https://developer.zendesk.com/rest_api/docs/chat/agents#list-agents) \(Incremental\)
- [Agent Timelines](https://developer.zendesk.com/rest_api/docs/chat/incremental_export#incremental-agent-timeline-export) \(Incremental\)
- [Chats](https://developer.zendesk.com/rest_api/docs/chat/chats#list-chats)
- [Shortcuts](https://developer.zendesk.com/rest_api/docs/chat/shortcuts#list-shortcuts)
- [Triggers](https://developer.zendesk.com/rest_api/docs/chat/triggers#list-triggers)
- [Bans](https://developer.zendesk.com/rest_api/docs/chat/bans#list-bans) \(Incremental\)
- [Departments](https://developer.zendesk.com/rest_api/docs/chat/departments#list-departments)
- [Goals](https://developer.zendesk.com/rest_api/docs/chat/goals#list-goals)
- [Skills](https://developer.zendesk.com/rest_api/docs/chat/skills#list-skills)
- [Roles](https://developer.zendesk.com/rest_api/docs/chat/roles#list-roles)
- [Routing Settings](https://developer.zendesk.com/rest_api/docs/chat/routing_settings#show-account-routing-settings)

## Performance considerations

The connector is restricted by Zendesk's [requests limitation](https://developer.zendesk.com/rest_api/docs/voice-api/introduction#rate-limits).

## Data type map

| Integration Type | Airbyte Type |
| :--------------- | :----------- |
| `string`         | `string`     |
| `number`         | `number`     |
| `array`          | `array`      |
| `object`         | `object`     |


## Build instructions
### Build your own connector image
This connector is built using our dynamic built process.
The base image used to build it is defined within the metadata.yaml file under the `connectorBuildOptions`.
The build logic is defined using [Dagger](https://dagger.io/) [here](https://github.com/airbytehq/airbyte/blob/master/airbyte-ci/connectors/pipelines/pipelines/builds/python_connectors.py).
It does not rely on a Dockerfile.

If you would like to patch our connector and build your own a simple approach would be:

1. Create your own Dockerfile based on the latest version of the connector image.
```Dockerfile
FROM airbyte/source-zendesk-chat:latest

COPY . ./airbyte/integration_code
RUN pip install ./airbyte/integration_code

# The entrypoint and default env vars are already set in the base image
# ENV AIRBYTE_ENTRYPOINT "python /airbyte/integration_code/main.py"
# ENTRYPOINT ["python", "/airbyte/integration_code/main.py"]
```
Please use this as an example. This is not optimized.

2. Build your image:
```bash
docker build -t airbyte/source-zendesk-chat:dev .
# Running the spec command against your patched connector
docker run airbyte/source-zendesk-chat:dev spec
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

| Version | Date       | Pull Request                                             | Subject                                                                                                          |
| :------ | :--------- | :------------------------------------------------------- | :--------------------------------------------------------------------------------------------------------------- |
| 0.2.0 | 2023-09-18 | [30528](https://github.com/airbytehq/airbyte/pull/30528) | Use our base image and remove Dockerfile |
| 0.1.14  | 2023-02-10 | [24190](https://github.com/airbytehq/airbyte/pull/24190) | Fix remove too high min/max from account stream                                                                  |
| 0.1.13  | 2023-02-10 | [22819](https://github.com/airbytehq/airbyte/pull/22819) | Specified date formatting in specification                                                                       |
| 0.1.12  | 2023-01-27 | [22026](https://github.com/airbytehq/airbyte/pull/22026) | Set `AvailabilityStrategy` for streams explicitly to `None`                                                      |
| 0.1.11  | 2022-10-18 | [17745](https://github.com/airbytehq/airbyte/pull/17745) | Add Engagements Stream and fix infity looping                                                                    |
| 0.1.10  | 2022-09-28 | [17326](https://github.com/airbytehq/airbyte/pull/17326) | Migrate to per-stream states.                                                                                    |
| 0.1.9   | 2022-08-23 | [15879](https://github.com/airbytehq/airbyte/pull/15879) | Corrected specification and stream schemas to support backward capability                                        |
| 0.1.8   | 2022-06-28 | [13387](https://github.com/airbytehq/airbyte/pull/13387) | Add state checkpoint to allow long runs                                                                          |
| 0.1.7   | 2022-05-25 | [12883](https://github.com/airbytehq/airbyte/pull/12883) | Pass timeout in request to prevent a stuck connection                                                            |
| 0.1.6   | 2021-12-15 | [7313](https://github.com/airbytehq/airbyte/pull/7313)   | Add support of `OAuth 2.0` authentication. Fixed the issue with `created_at` can now be `null` for `bans` stream |
| 0.1.5   | 2021-12-06 | [8425](https://github.com/airbytehq/airbyte/pull/8425)   | Update title, description fields in spec                                                                         |
| 0.1.4   | 2021-11-22 | [8166](https://github.com/airbytehq/airbyte/pull/8166)   | Make `Chats` stream incremental + add tests for all streams                                                      |
| 0.1.3   | 2021-10-21 | [7210](https://github.com/airbytehq/airbyte/pull/7210)   | Chats stream is only getting data from first page                                                                |
| 0.1.2   | 2021-08-17 | [5476](https://github.com/airbytehq/airbyte/pull/5476)   | Correct field unread to boolean type                                                                             |
| 0.1.1   | 2021-06-09 | [3973](https://github.com/airbytehq/airbyte/pull/3973)   | Add `AIRBYTE_ENTRYPOINT` for Kubernetes support                                                                  |
| 0.1.0   | 2021-05-03 | [3088](https://github.com/airbytehq/airbyte/pull/3088)   | Initial release                                                                                                  |
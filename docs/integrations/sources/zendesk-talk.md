# Zendesk Talk

## Prerequisites

* Zendesk API Token or Zendesk OAuth Client
* Zendesk Email (For API Token authentication)
* Zendesk Subdomain

## Setup guide

### Step 1: Set up Zendesk

Generate a API access token as described in [Zendesk docs](https://support.zendesk.com/hc/en-us/articles/226022787-Generating-a-new-API-token-)

We recommend creating a restricted, read-only key specifically for Airbyte access. This will allow you to control which resources Airbyte should be able to access.

Another option is to use OAuth2.0 for authentication. See [Zendesk docs](https://support.zendesk.com/hc/en-us/articles/4408845965210-Using-OAuth-authentication-with-your-application) for details.

<!-- env:cloud -->
### Step 2: Set up the Zendesk Talk connector in Airbyte

**For Airbyte Cloud:**

1. [Log into your Airbyte Cloud](https://cloud.airbyte.com/workspaces) account.
2. In the left navigation bar, click **Sources**. In the top-right corner, click **+new source**.
3. On the Set up the source page, enter the name for the Zendesk Talk connector and select **Zendesk Talk** from the Source type dropdown.
4. Fill in the rest of the fields:
   - *Subdomain*
   - *Authentication (API Token / OAuth2.0)*
   - *Start Date*
5. Click **Set up source**
<!-- /env:cloud -->

## Supported sync modes

The **Zendesk Talk** source connector supports the following [sync modes](https://docs.airbyte.com/cloud/core-concepts#connection-sync-modes):
* Full Refresh
* Incremental Sync

## Supported Streams

This Source is capable of syncing the following core Streams:

* [Account Overview](https://developer.zendesk.com/rest_api/docs/voice-api/stats#show-account-overview)
* [Addresses](https://developer.zendesk.com/rest_api/docs/voice-api/phone_numbers#list-phone-numbers)
* [Agents Activity](https://developer.zendesk.com/rest_api/docs/voice-api/stats#list-agents-activity)
* [Agents Overview](https://developer.zendesk.com/rest_api/docs/voice-api/stats#show-agents-overview)
* [Calls](https://developer.zendesk.com/rest_api/docs/voice-api/incremental_exports#incremental-calls-export) \(Incremental sync\)
* [Call Legs](https://developer.zendesk.com/rest_api/docs/voice-api/incremental_exports#incremental-call-legs-export) \(Incremental sync\)
* [Current Queue Activity](https://developer.zendesk.com/rest_api/docs/voice-api/stats#show-current-queue-activity)
* [Greeting Categories](https://developer.zendesk.com/rest_api/docs/voice-api/greetings#list-greeting-categories)
* [Greetings](https://developer.zendesk.com/rest_api/docs/voice-api/greetings#list-greetings)
* [IVRs](https://developer.zendesk.com/rest_api/docs/voice-api/ivrs#list-ivrs)
* [IVR Menus](https://developer.zendesk.com/rest_api/docs/voice-api/ivrs#list-ivrs)
* [IVR Routes](https://developer.zendesk.com/rest_api/docs/voice-api/ivr_routes#list-ivr-routes)
* [Phone Numbers](https://developer.zendesk.com/rest_api/docs/voice-api/phone_numbers#list-phone-numbers)

## Performance considerations

The connector is restricted by normal Zendesk [requests limitation](https://developer.zendesk.com/rest_api/docs/voice-api/introduction#rate-limits).

The Zendesk connector should not run into Zendesk API limitations under normal usage. Please [create an issue](https://github.com/airbytehq/airbyte/issues) if you see any rate limit issues that are not automatically retried successfully.

## Data type map

| Integration Type | Airbyte Type | Notes |
| :------- | :------- | :--- |
| `string` | `string` |      |
| `number` | `number` |      |
| `array`  | `array`  |      |
| `object` | `object` |      |



## Build instructions
### Build your own connector image
This connector is built using our dynamic built process.
The base image used to build it is defined within the metadata.yaml file under the `connectorBuildOptions`.
The build logic is defined using [Dagger](https://dagger.io/) [here](https://github.com/airbytehq/airbyte/blob/master/airbyte-ci/connectors/pipelines/pipelines/builds/python_connectors.py).
It does not rely on a Dockerfile.

If you would like to patch our connector and build your own a simple approach would be:

1. Create your own Dockerfile based on the latest version of the connector image.
```Dockerfile
FROM airbyte/source-zendesk-talk:latest

COPY . ./airbyte/integration_code
RUN pip install ./airbyte/integration_code

# The entrypoint and default env vars are already set in the base image
# ENV AIRBYTE_ENTRYPOINT "python /airbyte/integration_code/main.py"
# ENTRYPOINT ["python", "/airbyte/integration_code/main.py"]
```
Please use this as an example. This is not optimized.

2. Build your image:
```bash
docker build -t airbyte/source-zendesk-talk:dev .
# Running the spec command against your patched connector
docker run airbyte/source-zendesk-talk:dev spec
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


| Version | Date       | Pull Request | Subject                           |
|:--------|:-----------| :-----       |:----------------------------------|
| 0.2.0 | 2023-09-18 | [30528](https://github.com/airbytehq/airbyte/pull/30528) | Use our base image and remove Dockerfile |
| `0.1.9` | 2023-08-03 | [29031](https://github.com/airbytehq/airbyte/pull/29031) | Reverted `advancedAuth` spec changes |
| `0.1.8` | 2023-08-01 | [28910](https://github.com/airbytehq/airbyte/pull/28910) | Updated `advancedAuth` broken references |
| `0.1.7` | 2023-02-10 | [22815](https://github.com/airbytehq/airbyte/pull/22815) | Specified date formatting in specification                                                     |
| `0.1.6` | 2023-01-27 | [22028](https://github.com/airbytehq/airbyte/pull/22028) | Set `AvailabilityStrategy` for streams explicitly to `None`                                                     |
| `0.1.5` | 2022-09-29 | [17362](https://github.com/airbytehq/airbyte/pull/17362) | always use the latest CDK version |
| `0.1.4` | 2022-08-19 | [15764](https://github.com/airbytehq/airbyte/pull/15764) | Support OAuth2.0                  |
| `0.1.3` | 2021-11-11 | [7173](https://github.com/airbytehq/airbyte/pull/7173)   | Fix pagination and migrate to CDK |
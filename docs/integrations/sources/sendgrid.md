# Sendgrid

This page contains the setup guide and reference information for the Sendgrid source connector.

## Prerequisites

* API Key

## Setup guide
### Step 1: Set up Sendgrid

* Sendgrid Account
* [Create Sendgrid API Key](https://docs.sendgrid.com/ui/account-and-settings/api-keys#creating-an-api-key) with the following permissions:
  * Read-only access to all resources
  * Full access to marketing resources

## Step 2: Set up the Sendgrid connector in Airbyte

### For Airbyte Cloud:

1. [Log into your Airbyte Cloud](https://cloud.airbyte.com/workspaces) account.
2. In the left navigation bar, click **Sources**. In the top-right corner, click **+new source**.
3. On the Set up the source page, enter the name for the Sendgrid connector and select **Sendgrid** from the Source type dropdown.
4. Enter your `apikey`.
5. Enter your `start_time`. 
6. Click **Set up source**.

### For Airbyte OSS:

1. Navigate to the Airbyte Open Source dashboard.
2. Set the name for your source. 
3. Enter your `apikey`.
4. Enter your `start_time`. 
5. Click **Set up source**.

## Supported sync modes

The Sendgrid source connector supports the following [sync modes](https://docs.airbyte.com/cloud/core-concepts#connection-sync-modes):

* [Full Refresh - Overwrite](https://docs.airbyte.com/understanding-airbyte/connections/full-refresh-overwrite/)
* [Full Refresh - Append](https://docs.airbyte.com/understanding-airbyte/connections/full-refresh-append)
* [Incremental - Append](https://docs.airbyte.com/understanding-airbyte/connections/incremental-append)

## Supported Streams

* [Campaigns](https://docs.sendgrid.com/api-reference/campaigns-api/retrieve-all-campaigns) 
* [Lists](https://docs.sendgrid.com/api-reference/lists/get-all-lists) 
* [Contacts](https://docs.sendgrid.com/api-reference/contacts/export-contacts) 
* [Stats automations](https://docs.sendgrid.com/api-reference/marketing-campaign-stats/get-all-automation-stats) 
* [Segments](https://docs.sendgrid.com/api-reference/segmenting-contacts/get-list-of-segments) 
* [Single Sends](https://docs.sendgrid.com/api-reference/marketing-campaign-stats/get-all-single-sends-stats) 
* [Templates](https://docs.sendgrid.com/api-reference/transactional-templates/retrieve-paged-transactional-templates) 
* [Global suppression](https://docs.sendgrid.com/api-reference/suppressions-global-suppressions/retrieve-all-global-suppressions) \(Incremental\)
* [Suppression groups](https://docs.sendgrid.com/api-reference/suppressions-unsubscribe-groups/retrieve-all-suppression-groups-associated-with-the-user)
* [Suppression group members](https://docs.sendgrid.com/api-reference/suppressions-suppressions/retrieve-all-suppressions) 
* [Blocks](https://docs.sendgrid.com/api-reference/blocks-api/retrieve-all-blocks) \(Incremental\)
* [Bounces](https://docs.sendgrid.com/api-reference/bounces-api/retrieve-all-bounces) \(Incremental\)
* [Invalid emails](https://docs.sendgrid.com/api-reference/invalid-e-mails-api/retrieve-all-invalid-emails) \(Incremental\)
* [Spam reports](https://docs.sendgrid.com/api-reference/spam-reports-api/retrieve-all-spam-reports)


## Connector-specific features & highlights, if any

We recommend creating a key specifically for Airbyte access. This will allow you to control which resources Airbyte should be able to access. The API key should be read-only on all resources except Marketing, where it needs Full Access.
Sendgrid provides two different kinds of marketing campaigns, "legacy marketing campaigns" and "new marketing campaigns". **Legacy marketing campaigns are not supported by this source connector**. 
If you are seeing a `403 FORBIDDEN error message for https://api.sendgrid.com/v3/marketing/campaigns`, it might be because your SendGrid account uses legacy marketing campaigns.

## Performance considerations

The connector is restricted by normal Sendgrid [requests limitation](https://sendgrid.com/docs/API_Reference/Web_API_v3/How_To_Use_The_Web_API_v3/rate_limits.html).


## Build instructions
### Build your own connector image
This connector is built using our dynamic built process.
The base image used to build it is defined within the metadata.yaml file under the `connectorBuildOptions`.
The build logic is defined using [Dagger](https://dagger.io/) [here](https://github.com/airbytehq/airbyte/blob/master/airbyte-ci/connectors/pipelines/pipelines/builds/python_connectors.py).
It does not rely on a Dockerfile.

If you would like to patch our connector and build your own a simple approach would be:

1. Create your own Dockerfile based on the latest version of the connector image.
```Dockerfile
FROM airbyte/source-sendgrid:latest

COPY . ./airbyte/integration_code
RUN pip install ./airbyte/integration_code

# The entrypoint and default env vars are already set in the base image
# ENV AIRBYTE_ENTRYPOINT "python /airbyte/integration_code/main.py"
# ENTRYPOINT ["python", "/airbyte/integration_code/main.py"]
```
Please use this as an example. This is not optimized.

2. Build your image:
```bash
docker build -t airbyte/source-sendgrid:dev .
# Running the spec command against your patched connector
docker run airbyte/source-sendgrid:dev spec
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

| Version | Date       | Pull Request                                             | Subject                                                                                                                                                                                                                                           |
|:--------|:-----------|:---------------------------------------------------------|:--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| 0.5.0 | 2023-09-18 | [30528](https://github.com/airbytehq/airbyte/pull/30528) | Use our base image and remove Dockerfile |
| 0.4.0   | 2023-05-19 | [23959](https://github.com/airbytehq/airbyte/pull/23959) | Add `unsubscribe_groups`stream 
| 0.3.1   | 2023-01-27 | [21939](https://github.com/airbytehq/airbyte/pull/21939) | Fix contacts missing records; Remove Messages stream                                                                                                                                                                                              |
| 0.3.0   | 2023-01-25 | [21587](https://github.com/airbytehq/airbyte/pull/21587) | Make sure spec works as expected in UI - make start_time parameter an ISO string instead of an integer interpreted as timestamp (breaking, update your existing connections and set the start_time parameter to ISO 8601 date time string in UTC) |
| 0.2.16  | 2022-11-02 | [18847](https://github.com/airbytehq/airbyte/pull/18847) | Skip the stream on `400, 401 - authorization required` with log message                                                                                                                                                                           |
| 0.2.15  | 2022-10-19 | [18182](https://github.com/airbytehq/airbyte/pull/18182) | Mark the sendgrid api key secret in the spec                                                                                                                                                                                                      |
| 0.2.14  | 2022-09-07 | [16400](https://github.com/airbytehq/airbyte/pull/16400) | Change Start Time config parameter to datetime string                                                                                                                                                                                             |
| 0.2.13  | 2022-08-29 | [16112](https://github.com/airbytehq/airbyte/pull/16112) | Revert back to Python CDK                                                                                                                                                                                                                         |
| 0.2.12  | 2022-08-24 | [15911](https://github.com/airbytehq/airbyte/pull/15911) | Bugfix to allowing reading schemas at runtime                                                                                                                                                                                                     |
| 0.2.11  | 2022-08-19 | [15800](https://github.com/airbytehq/airbyte/pull/15800) | Bugfix to allow reading sentry.yaml at runtime                                                                                                                                                                                                    |
| 0.2.10  | 2022-08-17 | [15734](https://github.com/airbytehq/airbyte/pull/15734) | Fix yaml based on the new schema validator                                                                                                                                                                                                        |
| 0.2.9   | 2022-08-11 | [15257](https://github.com/airbytehq/airbyte/pull/15257) | Migrate to config-based framework                                                                                                                                                                                                                 |
| 0.2.8   | 2022-06-07 | [13571](https://github.com/airbytehq/airbyte/pull/13571) | Add Message stream                                                                                                                                                                                                                                |
| 0.2.7   | 2021-09-08 | [5910](https://github.com/airbytehq/airbyte/pull/5910)   | Add Single Sends Stats stream                                                                                                                                                                                                                     |
| 0.2.6   | 2021-07-19 | [4839](https://github.com/airbytehq/airbyte/pull/4839)   | Gracefully handle malformed responses from the API                                                                                                                                                                                                |
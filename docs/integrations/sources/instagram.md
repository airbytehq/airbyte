# Instagram

This page contains the setup guide and reference information for the Instagram source connector.

## Prerequisites

- [Meta for Developers account](https://developers.facebook.com)
- [Instagram business account](https://www.facebook.com/business/help/898752960195806) to your Facebook page
- [Instagram Graph API](https://developers.facebook.com/docs/instagram-api/) to your Facebook app
- [Facebook OAuth Reference](https://developers.facebook.com/docs/instagram-basic-display-api/reference)
- [Facebook ad account ID number](https://www.facebook.com/business/help/1492627900875762) (you'll use this to configure Instagram as a source in Airbyte)

## Setup Guide

### Set up the Instagram connector in Airbyte

<!-- env:cloud -->

**For Airbyte Cloud:**

1. Log in to your [Airbyte Cloud](https://cloud.airbyte.com/workspaces) account.
2. Click **Sources** and then click **+ New source**.
3. On the Set up the source page, select **Instagram** from the **Source type** dropdown.
4. Enter a name for your source.
5. Click **Authenticate your Instagram account**.
6. Log in and authorize the Instagram account.
7. Enter the **Start Date** in YYYY-MM-DDTHH:mm:ssZ format. All data generated after this date will be replicated. If this field is blank, Airbyte will replicate all data.
8. Click **Set up source**.
<!-- /env:cloud -->

<!-- env:oss -->

**For Airbyte Open Source:**

1. Log in to your Airbyte Open Source account.
2. Click **Sources** and then click **+ New source**.
3. On the Set up the source page, select **Instagram** from the **Source type** dropdown.
4. Enter a name for your source.
5. Click **Authenticate your Instagram account**.
6. Log in and authorize the Instagram account.
7. Enter the **Start Date** in YYYY-MM-DDTHH:mm:ssZ format. All data generated after this date will be replicated. If this field is blank, Airbyte will replicate all data.
8. Click **Set up source**.
<!-- /env:oss -->

## Supported sync modes

The Instagram source connector supports the following [sync modes](https://docs.airbyte.com/cloud/core-concepts#connection-sync-modes):

- [Full Refresh - Overwrite](https://docs.airbyte.com/understanding-airbyte/connections/full-refresh-overwrite/)
- [Full Refresh - Append](https://docs.airbyte.com/understanding-airbyte/connections/full-refresh-append)
- [Incremental - Append](https://docs.airbyte.com/understanding-airbyte/connections/incremental-append)
- [Incremental - Append + Deduped](https://docs.airbyte.com/understanding-airbyte/connections/incremental-append-deduped)

:::note

Incremental sync modes are only available for the [User Insights](https://developers.facebook.com/docs/instagram-api/reference/ig-user/insights) stream.

:::

## Supported Streams

The Instagram source connector supports the following streams. For more information, see the [Instagram Graph API](https://developers.facebook.com/docs/instagram-api/) and [Instagram Insights API documentation](https://developers.facebook.com/docs/instagram-api/guides/insights/).

- [User](https://developers.facebook.com/docs/instagram-api/reference/ig-user)
  - [User Insights](https://developers.facebook.com/docs/instagram-api/reference/ig-user/insights)
- [Media](https://developers.facebook.com/docs/instagram-api/reference/ig-user/media)
  - [Media Insights](https://developers.facebook.com/docs/instagram-api/reference/ig-media/insights)
- [Stories](https://developers.facebook.com/docs/instagram-api/reference/ig-user/stories/)
  - [Story Insights](https://developers.facebook.com/docs/instagram-api/reference/ig-media/insights)

### Rate Limiting and Performance Considerations

Instagram limits the number of requests that can be made at a time, but the Instagram connector gracefully handles rate limiting. See Facebook's [documentation on rate limiting](https://developers.facebook.com/docs/graph-api/overview/rate-limiting/#instagram-graph-api) for more information.

## Data type map

AirbyteRecords are required to conform to the [Airbyte type](https://docs.airbyte.com/understanding-airbyte/supported-data-types/) system. This means that all sources must produce schemas and records within these types and all destinations must handle records that conform to this type system.

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
FROM airbyte/source-instagram:latest

COPY . ./airbyte/integration_code
RUN pip install ./airbyte/integration_code

# The entrypoint and default env vars are already set in the base image
# ENV AIRBYTE_ENTRYPOINT "python /airbyte/integration_code/main.py"
# ENTRYPOINT ["python", "/airbyte/integration_code/main.py"]
```
Please use this as an example. This is not optimized.

2. Build your image:
```bash
docker build -t airbyte/source-instagram:dev .
# Running the spec command against your patched connector
docker run airbyte/source-instagram:dev spec
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

| Version | Date       | Pull Request                                             | Subject                                                                                                                   |
| :------ | :--------- | :------------------------------------------------------- | :------------------------------------------------------------------------------------------------------------------------ |
| 1.1.0 | 2023-09-18 | [30528](https://github.com/airbytehq/airbyte/pull/30528) | Use our base image and remove Dockerfile |
| 1.0.11  | 2023-08-03 | [29031](https://github.com/airbytehq/airbyte/pull/29031) | Reverted `advancedAuth` spec changes                                                                                      |
| 1.0.10  | 2023-08-01 | [28910](https://github.com/airbytehq/airbyte/pull/28910) | Updated `advancedAuth` broken references                                                                                  |
| 1.0.9   | 2023-07-01 | [27908](https://github.com/airbytehq/airbyte/pull/27908) | Fix bug when `user_lifetime_insights` stream returns `Key Error (end_time)`, refactored `state` to use `IncrementalMixin` |
| 1.0.8   | 2023-05-26 | [26767](https://github.com/airbytehq/airbyte/pull/26767) | Handle permission error for `insights`                                                                                    |
| 1.0.7   | 2023-05-26 | [26656](https://github.com/airbytehq/airbyte/pull/26656) | Remove `authSpecification` from connector specification in favour of `advancedAuth`                                       |
| 1.0.6   | 2023-03-28 | [26599](https://github.com/airbytehq/airbyte/pull/26599) | Handle error for Media posted before business account conversion                                                          |
| 1.0.5   | 2023-03-28 | [24634](https://github.com/airbytehq/airbyte/pull/24634) | Add user-friendly message for no instagram_business_accounts case                                                         |
| 1.0.4   | 2023-03-15 | [23671](https://github.com/airbytehq/airbyte/pull/23671) | Add info about main permissions in spec and doc links in error message to navigate user                                   |
| 1.0.3   | 2023-03-14 | [24043](https://github.com/airbytehq/airbyte/pull/24043) | Do not emit incomplete records for `user_insights` stream                                                                 |
| 1.0.2   | 2023-03-14 | [24042](https://github.com/airbytehq/airbyte/pull/24042) | Test publish flow                                                                                                         |
| 1.0.1   | 2023-01-19 | [21602](https://github.com/airbytehq/airbyte/pull/21602) | Handle abnormally large state values                                                                                      |
| 1.0.0   | 2022-09-23 | [17110](https://github.com/airbytehq/airbyte/pull/17110) | Remove custom read function and migrate to per-stream state                                                               |
| 0.1.11  | 2022-09-08 | [16428](https://github.com/airbytehq/airbyte/pull/16428) | Fix requests metrics for Reels media product type                                                                         |
| 0.1.10  | 2022-09-05 | [16340](https://github.com/airbytehq/airbyte/pull/16340) | Update to latest version of the CDK (v0.1.81)                                                                             |
| 0.1.9   | 2021-09-30 | [6438](https://github.com/airbytehq/airbyte/pull/6438)   | Annotate Oauth2 flow initialization parameters in connector specification                                                 |
| 0.1.8   | 2021-08-11 | [5354](https://github.com/airbytehq/airbyte/pull/5354)   | Added check for empty state and fixed tests                                                                               |
| 0.1.7   | 2021-07-19 | [4805](https://github.com/airbytehq/airbyte/pull/4805)   | Add support for previous `STATE` format                                                                                   |
| 0.1.6   | 2021-07-07 | [4210](https://github.com/airbytehq/airbyte/pull/4210)   | Refactor connector to use CDK: - improve error handling - fix sync fail with HTTP status 400 - integrate SAT              |
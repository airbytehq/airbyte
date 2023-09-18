# Recharge

This source can sync data for the [Recharge API](https://developer.rechargepayments.com/).
This page guides you through the process of setting up the Recharge source connector.

## Prerequisites

- A Recharge account with permission to access data from accounts you want to sync.
- Recharge API Token

## Setup guide

### Step 1: Set up Recharge

Please read [How to generate your API token](https://support.rechargepayments.com/hc/en-us/articles/360008829993-ReCharge-API).

### Step 2: Set up the source connector in Airbyte

<!-- env:cloud -->

**For Airbyte Cloud:**

1. [Log into your Airbyte Cloud](https://cloud.airbyte.com/workspaces) account.
2. In the left navigation bar, click **Sources**. In the top-right corner, click **+ new source**.
3. On the source setup page, select **Recharge** from the Source type dropdown and enter a name for this connector.
4. Choose required `Start date`
5. Enter your `Access Token`.
6. click `Set up source`.
<!-- /env:cloud -->

<!-- env:oss -->

**For Airbyte Open Source:**

1. Go to local Airbyte page.
2. In the left navigation bar, click **Sources**. In the top-right corner, click **+ new source**.
3. On the source setup page, select **Recharge** from the Source type dropdown and enter a name for this connector.
4. Choose required `Start date`
5. Enter your `Access Token` generated from `Step 1`.
6. click `Set up source`.
<!-- /env:oss -->

## Supported sync modes

The Recharge supports full refresh and incremental sync.

| Feature           | Supported? |
| :---------------- | :--------- |
| Full Refresh Sync | Yes        |
| Incremental Sync  | Yes        |
| SSL connection    | Yes        |

## Supported Streams

Several output streams are available from this source:

- [Addresses](https://developer.rechargepayments.com/v1-shopify?python#list-addresses) \(Incremental sync\)
- [Charges](https://developer.rechargepayments.com/v1-shopify?python#list-charges) \(Incremental sync\)
- [Collections](https://developer.rechargepayments.com/v1-shopify)
- [Customers](https://developer.rechargepayments.com/v1-shopify?python#list-customers) \(Incremental sync\)
- [Discounts](https://developer.rechargepayments.com/v1-shopify?python#list-discounts) \(Incremental sync\)
- [Metafields](https://developer.rechargepayments.com/v1-shopify?python#list-metafields)
- [Onetimes](https://developer.rechargepayments.com/v1-shopify?python#list-onetimes) \(Incremental sync\)
- [Orders](https://developer.rechargepayments.com/v1-shopify?python#list-orders) \(Incremental sync\)
- [Products](https://developer.rechargepayments.com/v1-shopify?python#list-products)
- [Shop](https://developer.rechargepayments.com/v1-shopify?python#shop)
- [Subscriptions](https://developer.rechargepayments.com/v1-shopify?python#list-subscriptions) \(Incremental sync\)

If there are more endpoints you'd like Airbyte to support, please [create an issue.](https://github.com/airbytehq/airbyte/issues/new/choose)

### Performance considerations

The Recharge connector should gracefully handle Recharge API limitations under normal usage. Please [create an issue](https://github.com/airbytehq/airbyte/issues) if you see any rate limit issues that are not automatically retried successfully.


## Build instructions
### Build your own connector image
This connector is built using our dynamic built process.
The base image used to build it is defined within the metadata.yaml file under the `connectorBuildOptions`.
The build logic is defined using [Dagger](https://dagger.io/) [here](https://github.com/airbytehq/airbyte/blob/master/airbyte-ci/connectors/pipelines/pipelines/builds/python_connectors.py).
It does not rely on a Dockerfile.

If you would like to patch our connector and build your own a simple approach would be:

1. Create your own Dockerfile based on the latest version of the connector image.
```Dockerfile
FROM airbyte/source-recharge:latest

COPY . ./airbyte/integration_code
RUN pip install ./airbyte/integration_code

# The entrypoint and default env vars are already set in the base image
# ENV AIRBYTE_ENTRYPOINT "python /airbyte/integration_code/main.py"
# ENTRYPOINT ["python", "/airbyte/integration_code/main.py"]
```
Please use this as an example. This is not optimized.

2. Build your image:
```bash
docker build -t airbyte/source-recharge:dev .
# Running the spec command against your patched connector
docker run airbyte/source-recharge:dev spec
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

| Version | Date       | Pull Request                                             | Subject                                                                                   |
|:--------|:-----------|:---------------------------------------------------------|:------------------------------------------------------------------------------------------|
| 1.1.0 | 2023-09-18 | [30528](https://github.com/airbytehq/airbyte/pull/30528) | Use our base image and remove Dockerfile |
| 1.0.1   | 2023-08-30 | [29992](https://github.com/airbytehq/airbyte/pull/29992) | Revert for orders stream to use old API version 2021-01                                   |
| 1.0.0   | 2023-06-22 | [27612](https://github.com/airbytehq/airbyte/pull/27612) | Change data type of the `shopify_variant_id_not_found` field of the `Charges` stream      |
| 0.2.10  | 2023-06-20 | [27503](https://github.com/airbytehq/airbyte/pull/27503) | Update API version to 2021-11                                                             |      
| 0.2.9   | 2023-04-10 | [25009](https://github.com/airbytehq/airbyte/pull/25009) | Fix owner slicing for `Metafields` stream                                                 |      
| 0.2.8   | 2023-04-07 | [24990](https://github.com/airbytehq/airbyte/pull/24990) | Add slicing to connector                                                                  |      
| 0.2.7   | 2023-02-13 | [22901](https://github.com/airbytehq/airbyte/pull/22901) | Specified date formatting in specification                                                |      
| 0.2.6   | 2023-02-21 | [22473](https://github.com/airbytehq/airbyte/pull/22473) | Use default availability strategy                                                         |              
| 0.2.5   | 2023-01-27 | [22021](https://github.com/airbytehq/airbyte/pull/22021) | Set `AvailabilityStrategy` for streams explicitly to `None`                               |
| 0.2.4   | 2022-10-11 | [17822](https://github.com/airbytehq/airbyte/pull/17822) | Do not parse JSON in `should_retry`                                                       |
| 0.2.3   | 2022-10-11 | [17822](https://github.com/airbytehq/airbyte/pull/17822) | Do not parse JSON in `should_retry`                                                       |
| 0.2.2   | 2022-10-05 | [17608](https://github.com/airbytehq/airbyte/pull/17608) | Skip stream if we receive 403 error                                                       |
| 0.2.2   | 2022-09-28 | [17304](https://github.com/airbytehq/airbyte/pull/17304) | Migrate to per-stream state.                                                              |
| 0.2.1   | 2022-09-23 | [17080](https://github.com/airbytehq/airbyte/pull/17080) | Fix `total_weight` value to be `int` instead of `float`                                   |
| 0.2.0   | 2022-09-21 | [16959](https://github.com/airbytehq/airbyte/pull/16959) | Use TypeTransformer to reliably convert to schema declared data types                     |
| 0.1.8   | 2022-08-27 | [16045](https://github.com/airbytehq/airbyte/pull/16045) | Force total_weight to be an integer                                                       |
| 0.1.7   | 2022-07-24 | [14978](https://github.com/airbytehq/airbyte/pull/14978) | Set `additionalProperties` to True, to guarantee backward cababilities                    |
| 0.1.6   | 2022-07-21 | [14902](https://github.com/airbytehq/airbyte/pull/14902) | Increased test coverage, fixed broken `charges`, `orders` schemas, added state checkpoint |
| 0.1.5   | 2022-01-26 | [9808](https://github.com/airbytehq/airbyte/pull/9808)   | Update connector fields title/description                                                 |
| 0.1.4   | 2021-11-05 | [7626](https://github.com/airbytehq/airbyte/pull/7626)   | Improve 'backoff' for HTTP requests                                                       |
| 0.1.3   | 2021-09-17 | [6149](https://github.com/airbytehq/airbyte/pull/6149)   | Update `discount` and `order` schema                                                      |
| 0.1.2   | 2021-09-17 | [6149](https://github.com/airbytehq/airbyte/pull/6149)   | Change `cursor_field` for Incremental streams                                             |
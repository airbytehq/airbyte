# Waiteraid

This page contains the setup guide and reference information for the Waiteraid source connector.

## Prerequisites

You can find or create authentication tokens within [Waiteraid](https://app.waiteraid.com/api-docs/index.html#auth_call).

## Setup guide

## Step 1: Set up the Waiteraid connector in Airbyte

### For Airbyte Cloud:

1. [Log into your Airbyte Cloud](https://cloud.airbyte.com/workspaces) account.
2. In the left navigation bar, click **Sources**. In the top-right corner, click **+new source**.
3. On the Set up the source page, enter the name for the Waiteraid connector and select **Waiteraid** from the Source type dropdown.
4. Enter your `auth_token` - Waiteraid Authentication Token.
5. Enter your `restaurant ID` - The Waiteraid ID of the Restaurant you wanto sync.
6. Click **Set up source**.
<!-- env:oss -->

### For Airbyte OSS:

1. Navigate to the Airbyte Open Source dashboard.
2. Set the name for your source.
3. Enter your `auth_token` - Waiteraid Authentication Token.
4. Enter your `restaurant ID` - The Waiteraid ID of the Restaurant you wanto sync.
5. Click **Set up source**.

## Supported sync modes

The Waiteraid source connector supports the following [sync modes](https://docs.airbyte.com/cloud/core-concepts#connection-sync-modes):

| Feature           | Supported? |
| :---------------- | :--------- |
| Full Refresh Sync | Yes        |
| Incremental Sync  | No         |
| SSL connection    | No         |
| Namespaces        | No         |

<!-- /env:oss -->

## Supported Streams

- [Bookings](https://app.waiteraid.com/api-docs/index.html#api_get_bookings)

## Data type map

| Integration Type    | Airbyte Type |
| :------------------ | :----------- |
| `string`            | `string`     |
| `integer`, `number` | `number`     |
| `array`             | `array`      |
| `object`            | `object`     |

## Changelog

<details>
  <summary>Expand to review</summary>

| Version | Date       | Pull Request                                           | Subject               |
| :------ | :--------- | :----------------------------------------------------- | :-------------------- |
| 0.1.4 | 2024-06-22 | [40087](https://github.com/airbytehq/airbyte/pull/40087) | Update dependencies |
| 0.1.3 | 2024-06-06 | [39185](https://github.com/airbytehq/airbyte/pull/39185) | [autopull] Upgrade base image to v1.2.2 |
| 0.1.2 | 2024-05-28 | [38697](https://github.com/airbytehq/airbyte/pull/38697) | Make connector compatible with builder |
| 0.1.1 | 2024-05-20 | [38433](https://github.com/airbytehq/airbyte/pull/38433) | [autopull] base image + poetry + up_to_date |
| 0.1.0   | 2022-10-QQ | [QQQQ](https://github.com/airbytehq/airbyte/pull/QQQQ) | New Source: Waiteraid |

</details>

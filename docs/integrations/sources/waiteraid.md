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
| 0.2.8 | 2025-01-11 | [51386](https://github.com/airbytehq/airbyte/pull/51386) | Update dependencies |
| 0.2.7 | 2024-12-28 | [50810](https://github.com/airbytehq/airbyte/pull/50810) | Update dependencies |
| 0.2.6 | 2024-12-21 | [50372](https://github.com/airbytehq/airbyte/pull/50372) | Update dependencies |
| 0.2.5 | 2024-12-14 | [49770](https://github.com/airbytehq/airbyte/pull/49770) | Update dependencies |
| 0.2.4 | 2024-12-12 | [49405](https://github.com/airbytehq/airbyte/pull/49405) | Update dependencies |
| 0.2.3 | 2024-10-29 | [47835](https://github.com/airbytehq/airbyte/pull/47835) | Update dependencies |
| 0.2.2 | 2024-10-28 | [47610](https://github.com/airbytehq/airbyte/pull/47610) | Update dependencies |
| 0.2.1 | 2024-08-16 | [44196](https://github.com/airbytehq/airbyte/pull/44196) | Bump source-declarative-manifest version |
| 0.2.0 | 2024-08-14 | [44047](https://github.com/airbytehq/airbyte/pull/44047) | Refactor connector to manifest-only format |
| 0.1.14 | 2024-08-12 | [43789](https://github.com/airbytehq/airbyte/pull/43789) | Update dependencies |
| 0.1.13 | 2024-08-10 | [43568](https://github.com/airbytehq/airbyte/pull/43568) | Update dependencies |
| 0.1.12 | 2024-08-03 | [43242](https://github.com/airbytehq/airbyte/pull/43242) | Update dependencies |
| 0.1.11 | 2024-07-27 | [42762](https://github.com/airbytehq/airbyte/pull/42762) | Update dependencies |
| 0.1.10 | 2024-07-20 | [42207](https://github.com/airbytehq/airbyte/pull/42207) | Update dependencies |
| 0.1.9 | 2024-07-13 | [41777](https://github.com/airbytehq/airbyte/pull/41777) | Update dependencies |
| 0.1.8 | 2024-07-10 | [41506](https://github.com/airbytehq/airbyte/pull/41506) | Update dependencies |
| 0.1.7 | 2024-07-09 | [41135](https://github.com/airbytehq/airbyte/pull/41135) | Update dependencies |
| 0.1.6 | 2024-07-06 | [40794](https://github.com/airbytehq/airbyte/pull/40794) | Update dependencies |
| 0.1.5 | 2024-06-25 | [40311](https://github.com/airbytehq/airbyte/pull/40311) | Update dependencies |
| 0.1.4 | 2024-06-22 | [40087](https://github.com/airbytehq/airbyte/pull/40087) | Update dependencies |
| 0.1.3 | 2024-06-06 | [39185](https://github.com/airbytehq/airbyte/pull/39185) | [autopull] Upgrade base image to v1.2.2 |
| 0.1.2 | 2024-05-28 | [38697](https://github.com/airbytehq/airbyte/pull/38697) | Make connector compatible with builder |
| 0.1.1 | 2024-05-20 | [38433](https://github.com/airbytehq/airbyte/pull/38433) | [autopull] base image + poetry + up_to_date |
| 0.1.0   | 2022-10-QQ | [QQQQ](https://github.com/airbytehq/airbyte/pull/QQQQ) | New Source: Waiteraid |

</details>

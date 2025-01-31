# Recruitee

This page contains the setup guide and reference information for the [Recruitee](https://recruitee.com/) source connector.

You can find more information about the Recruitee REST API [here](https://docs.recruitee.com/reference/getting-started).

## Prerequisites

You can find your Company ID and find or create an API key within [Recruitee](https://docs.recruitee.com/reference/getting-started).

## Setup guide

## Step 1: Set up the Recruitee connector in Airbyte

### For Airbyte Cloud:

1. [Log into your Airbyte Cloud](https://cloud.airbyte.com/workspaces) account.
2. In the left navigation bar, click **Sources**. In the top-right corner, click **+new source**.
3. On the Set up the source page, enter the name for the Recruitee connector and select **Recruitee** from the Source type dropdown.
4. Enter your `company_id` - Recruitee Company ID.
5. Enter your `api_key` - Recruitee API key.
6. Click **Set up source**.

### For Airbyte OSS:

1. Navigate to the Airbyte Open Source dashboard.
2. Set the name for your source.
3. Enter your `company_id` - Recruitee Company ID.
4. Enter your `api_key` - Recruitee API key.
5. Click **Set up source**.

## Supported sync modes

The Recruitee source connector supports the following [sync modes](https://docs.airbyte.com/cloud/core-concepts#connection-sync-modes):

| Feature           | Supported? |
| :---------------- | :--------- |
| Full Refresh Sync | Yes        |
| Incremental Sync  | No         |
| SSL connection    | Yes        |
| Namespaces        | No         |

## Supported Streams

- [Candidates](https://docs.recruitee.com/reference/candidates-get)
- [Offers](https://docs.recruitee.com/reference/offers-get)
- [Departments](https://docs.recruitee.com/reference/departments-get)

## Changelog

<details>
  <summary>Expand to review</summary>

| Version | Date       | Pull Request                                             | Subject               |
|:--------|:-----------| :------------------------------------------------------- | :-------------------- |
| 0.2.10 | 2025-01-25 | [52475](https://github.com/airbytehq/airbyte/pull/52475) | Update dependencies |
| 0.2.9 | 2025-01-18 | [51852](https://github.com/airbytehq/airbyte/pull/51852) | Update dependencies |
| 0.2.8 | 2025-01-11 | [51298](https://github.com/airbytehq/airbyte/pull/51298) | Update dependencies |
| 0.2.7 | 2024-12-28 | [50689](https://github.com/airbytehq/airbyte/pull/50689) | Update dependencies |
| 0.2.6 | 2024-12-21 | [50263](https://github.com/airbytehq/airbyte/pull/50263) | Update dependencies |
| 0.2.5 | 2024-12-14 | [49701](https://github.com/airbytehq/airbyte/pull/49701) | Update dependencies |
| 0.2.4 | 2024-12-12 | [49074](https://github.com/airbytehq/airbyte/pull/49074) | Update dependencies |
| 0.2.3 | 2024-10-29 | [47924](https://github.com/airbytehq/airbyte/pull/47924) | Update dependencies |
| 0.2.2 | 2024-10-28 | [47522](https://github.com/airbytehq/airbyte/pull/47522) | Update dependencies |
| 0.2.1 | 2024-08-16 | [44196](https://github.com/airbytehq/airbyte/pull/44196) | Bump source-declarative-manifest version |
| 0.2.0 | 2024-08-14 | [44079](https://github.com/airbytehq/airbyte/pull/44079) | Refactor connector to manifest-only format |
| 0.1.14 | 2024-08-12 | [43810](https://github.com/airbytehq/airbyte/pull/43810) | Update dependencies |
| 0.1.13 | 2024-08-10 | [43508](https://github.com/airbytehq/airbyte/pull/43508) | Update dependencies |
| 0.1.12 | 2024-08-03 | [43264](https://github.com/airbytehq/airbyte/pull/43264) | Update dependencies |
| 0.1.11 | 2024-07-27 | [42605](https://github.com/airbytehq/airbyte/pull/42605) | Update dependencies |
| 0.1.10 | 2024-07-20 | [42268](https://github.com/airbytehq/airbyte/pull/42268) | Update dependencies |
| 0.1.9 | 2024-07-13 | [41930](https://github.com/airbytehq/airbyte/pull/41930) | Update dependencies |
| 0.1.8 | 2024-07-10 | [41388](https://github.com/airbytehq/airbyte/pull/41388) | Update dependencies |
| 0.1.7 | 2024-07-09 | [41265](https://github.com/airbytehq/airbyte/pull/41265) | Update dependencies |
| 0.1.6 | 2024-07-06 | [40792](https://github.com/airbytehq/airbyte/pull/40792) | Update dependencies |
| 0.1.5 | 2024-06-28 | [38744](https://github.com/airbytehq/airbyte/pull/38744) | Make connector compatible with Builder |
| 0.1.4 | 2024-06-25 | [40455](https://github.com/airbytehq/airbyte/pull/40455) | Update dependencies |
| 0.1.3 | 2024-06-22 | [40044](https://github.com/airbytehq/airbyte/pull/40044) | Update dependencies |
| 0.1.2 | 2024-06-06 | [39282](https://github.com/airbytehq/airbyte/pull/39282) | [autopull] Upgrade base image to v1.2.2 |
| 0.1.1 | 2024-05-20 | [38452](https://github.com/airbytehq/airbyte/pull/38452) | [autopull] base image + poetry + up_to_date |
| 0.1.0 | 2022-10-30 | [18671](https://github.com/airbytehq/airbyte/pull/18671) | New Source: Recruitee |

</details>

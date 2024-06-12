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
| :------ | :--------- | :------------------------------------------------------- | :-------------------- |
| 0.1.2 | 2024-06-06 | [39282](https://github.com/airbytehq/airbyte/pull/39282) | [autopull] Upgrade base image to v1.2.2 |
| 0.1.1 | 2024-05-20 | [38452](https://github.com/airbytehq/airbyte/pull/38452) | [autopull] base image + poetry + up_to_date |
| 0.1.0 | 2022-10-30 | [18671](https://github.com/airbytehq/airbyte/pull/18671) | New Source: Recruitee |

</details>

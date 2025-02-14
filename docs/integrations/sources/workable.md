# Workable

This page guides you through the process of setting up the Workable source connector.

## Prerequisites

You can find or create a Workable access token within the [Workable Integrations Settings page](https://test-432879.workable.com/backend/settings/integrations). See [this page](https://workable.readme.io/reference/generate-an-access-token#generate-an-api-access-token) for a step-by-step guide.

## Setup guide

## Step 1: Set up the Workable connector in Airbyte

### For Airbyte Cloud:

1. [Log into your Airbyte Cloud](https://cloud.airbyte.com/workspaces) account.
2. In the left navigation bar, click **Sources**. In the top-right corner, click **+new source**.
3. On the Set up the source page, enter the name for the Workable connector and select **Workable** from the Source type dropdown.
4. Enter your `api_token` - Workable Access Token.
5. Enter your `account_subdomain` - Sub-domain for your organization on Workable, e.g. https://YOUR_ACCOUNT_SUBDOMAIN.workable.com.
6. Enter your `created_after_date` - The earliest created at date from which you want to sync your Workable data.
7. Click **Set up source**.

### For Airbyte OSS:

1. Navigate to the Airbyte Open Source dashboard.
2. Set the name for your source.
3. Enter your `api_token` - Workable Access Token.
4. Enter your `account_subdomain` - Sub-domain for your organization on Workable, e.g. https://YOUR_ACCOUNT_SUBDOMAIN.workable.com.
5. Enter your `created_after_date` - The earliest created at date from which you want to sync your Workable data.
6. Click **Set up source**.

## Supported sync modes

The Workable source connector supports the following [sync modes](https://docs.airbyte.com/cloud/core-concepts#connection-sync-modes):

| Feature           | Supported? |
| :---------------- | :--------- |
| Full Refresh Sync | Yes        |
| Incremental Sync  | No         |
| SSL connection    | Yes        |
| Namespaces        | No         |

## Supported Streams

- [Jobs](https://workable.readme.io/reference/jobs)
- [Candidates](https://workable.readme.io/reference/job-candidates-index)
- [Stages](https://workable.readme.io/reference/stages)
- [Recruiters](https://workable.readme.io/reference/recruiters)

## Changelog

<details>
  <summary>Expand to review</summary>

| Version | Date       | Pull Request                                             | Subject              |
| :------ | :--------- | :------------------------------------------------------- | :------------------- |
| 0.2.5 | 2025-02-08 | [53568](https://github.com/airbytehq/airbyte/pull/53568) | Update dependencies |
| 0.2.4 | 2025-02-01 | [53034](https://github.com/airbytehq/airbyte/pull/53034) | Update dependencies |
| 0.2.3 | 2025-01-25 | [52449](https://github.com/airbytehq/airbyte/pull/52449) | Update dependencies |
| 0.2.2 | 2025-01-18 | [47642](https://github.com/airbytehq/airbyte/pull/47642) | Update dependencies |
| 0.2.1 | 2024-08-16 | [44196](https://github.com/airbytehq/airbyte/pull/44196) | Bump source-declarative-manifest version |
| 0.2.0 | 2024-08-14 | [44044](https://github.com/airbytehq/airbyte/pull/44044) | Refactor connector to manifest-only format |
| 0.1.14 | 2024-08-12 | [43765](https://github.com/airbytehq/airbyte/pull/43765) | Update dependencies |
| 0.1.13 | 2024-08-10 | [43520](https://github.com/airbytehq/airbyte/pull/43520) | Update dependencies |
| 0.1.12 | 2024-08-03 | [43146](https://github.com/airbytehq/airbyte/pull/43146) | Update dependencies |
| 0.1.11 | 2024-07-27 | [42772](https://github.com/airbytehq/airbyte/pull/42772) | Update dependencies |
| 0.1.10 | 2024-07-20 | [42290](https://github.com/airbytehq/airbyte/pull/42290) | Update dependencies |
| 0.1.9 | 2024-07-16 | [38343](https://github.com/airbytehq/airbyte/pull/38343) | Make compatable with the builder |
| 0.1.8 | 2024-07-13 | [41916](https://github.com/airbytehq/airbyte/pull/41916) | Update dependencies |
| 0.1.7 | 2024-07-10 | [41524](https://github.com/airbytehq/airbyte/pull/41524) | Update dependencies |
| 0.1.6 | 2024-07-09 | [41091](https://github.com/airbytehq/airbyte/pull/41091) | Update dependencies |
| 0.1.5 | 2024-07-06 | [41012](https://github.com/airbytehq/airbyte/pull/41012) | Update dependencies |
| 0.1.4 | 2024-06-25 | [40479](https://github.com/airbytehq/airbyte/pull/40479) | Update dependencies |
| 0.1.3 | 2024-06-22 | [39984](https://github.com/airbytehq/airbyte/pull/39984) | Update dependencies |
| 0.1.2 | 2024-06-06 | [39268](https://github.com/airbytehq/airbyte/pull/39268) | [autopull] Upgrade base image to v1.2.2 |
| 0.1.1 | 2024-05-21 | [38503](https://github.com/airbytehq/airbyte/pull/38503) | [autopull] base image + poetry + up_to_date |
| 0.1.0 | 2022-10-15 | [18033](https://github.com/airbytehq/airbyte/pull/18033) | New Source: Workable |

</details>

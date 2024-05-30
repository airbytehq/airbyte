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

| Version | Date       | Pull Request                                             | Subject              |
| :------ | :--------- | :------------------------------------------------------- | :------------------- |
| 0.1.0   | 2022-10-15 | [18033](https://github.com/airbytehq/airbyte/pull/18033) | New Source: Workable |

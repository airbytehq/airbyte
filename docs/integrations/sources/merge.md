# Merge

This page contains the setup guide and reference information for the [Merge](https://docs.merge.dev/ats/overview/) source

## Prerequisites

Access Token (which acts as bearer token) and linked accounts tokens are mandate for this connector to work, It could be seen at settings (Bearer ref - https://app.merge.dev/keys) and (Account token ref - https://app.merge.dev/keys).

## Setup guide

### Step 1: Set up Merge connection

- Link your other integrations with account credentials on accounts section (ref - https://app.merge.dev/linked-accounts/accounts)
- Get your bearer token on keys section (ref - https://app.merge.dev/keys)
- Setup params (All params are required)
- Available params
  - account_token: Linked account token seen after integration at linked account section
  - api_token: Bearer token seen at keys section, try to use production keys
  - start_date: Date filter for eligible streams

## Step 2: Set up the Merge connector in Airbyte

### For Airbyte Cloud:

1. [Log into your Airbyte Cloud](https://cloud.airbyte.io/workspaces) account.
2. In the left navigation bar, click **Sources**. In the top-right corner, click **+new source**.
3. On the Set up the source page, enter the name for the merge connector and select **Merge** from the Source type dropdown.
4. Enter your `account_token, api_token and start_date`.
5. Click **Set up source**.

### For Airbyte OSS:

1. Navigate to the Airbyte Open Source dashboard.
2. Set the name for your source.
3. Enter your `account_token, api_token and start_date`.
4. Click **Set up source**.

## Supported sync modes

The Merge source connector supports the following [sync modes](https://docs.airbyte.com/cloud/core-concepts#connection-sync-modes):

| Feature                       | Supported? |
| :---------------------------- | :--------- |
| Full Refresh Sync             | Yes        |
| Incremental Sync              | No         |
| Replicate Incremental Deletes | No         |
| SSL connection                | Yes        |
| Namespaces                    | No         |

## Supported Streams

- account_details
- activities
- applications
- attachments
- candidates
- departments
- eeocs
- interviews
- job-interview-stages
- jobs
- offers
- offices
- sync_status
- users

## API method example

GET https://api.merge.dev/api/ats/v1/account-details

## Performance considerations

Merge [API reference](https://api.merge.dev/api/ats/v1/) has v1 at present. The connector as default uses v1.

## Changelog

| Version | Date       | Pull Request                                       | Subject        |
| :------ | :--------- | :------------------------------------------------- | :------------- |
| 0.1.0   | 2023-04-18 | [Init](https://github.com/airbytehq/airbyte/pull/) | Initial commit |

# MailGun

This page contains the setup guide and reference information for the [MailGun](https://www.mailgun.com/) source connector.

## Prerequisites

Api key is mandate for this connector to work, It could be seen at Mailgun dashboard at settings, Navigate through API Keys section and click on the eye icon next to Private API key [See reference](https://documentation.mailgun.com/en/latest/api-intro.html#authentication-1).
Just pass the generated API key for establishing the connection.

## Setup guide

### Step 1: Set up MailGun connection

- Generate an API key (Example: 12345)
- Params (If specific info is needed)
- Available params
  - domain_region: Domain region code. 'EU' or 'US' are possible values. The default is 'US'.
  - start_date: UTC date and time in the format 2020-10-01 00:00:00. Any data before this date will not be replicated. If omitted, defaults to 3 days ago.

## Step 2: Set up the MailGun connector in Airbyte

### For Airbyte Cloud:

1. [Log into your Airbyte Cloud](https://cloud.airbyte.com/workspaces) account.
2. In the left navigation bar, click **Sources**. In the top-right corner, click **+new source**.
3. On the Set up the source page, enter the name for the MailGun connector and select **MailGun** from the Source type dropdown.
4. Enter your api_key as `private_key`.
5. Enter the params configuration if needed. Supported params are: domain_region, start_date.
6. Click **Set up source**.

### For Airbyte OSS:

1. Navigate to the Airbyte Open Source dashboard.
2. Set the name for your source.
3. Enter your api_key as `pivate_key`.
4. Enter the params configuration if needed. Supported params are: domain_region, start_date.
5. Click **Set up source**.

## Supported sync modes

The MailGun source connector supports the following [sync modes](https://docs.airbyte.com/cloud/core-concepts#connection-sync-modes):

| Feature                       | Supported? |
| :---------------------------- | :--------- |
| Full Refresh Sync             | Yes        |
| Incremental Sync              | Yes        |
| Replicate Incremental Deletes | No         |
| SSL connection                | Yes        |
| Namespaces                    | No         |

## Supported Streams

- domains
- events

## API method example

`GET https://api.mailgun.net/v3/domains`

## Performance considerations

MailGun's [API reference](https://documentation.mailgun.com/en/latest/api_reference.html) has v3 at present and v4 is at development. The connector as default uses v3.

## Changelog

| Version | Date       | Pull Request                                             | Subject                                     |
| :------ | :--------- | :------------------------------------------------------  | :------------------------------------------ |
| 0.1.1   | 2023-02-13 | [22939](https://github.com/airbytehq/airbyte/pull/22939) | Specified date formatting in specification  |
| 0.1.0   | 2021-11-09 | [8056](https://github.com/airbytehq/airbyte/pull/8056)   | New Source: Mailgun                         |

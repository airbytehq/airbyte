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
  - **Domain Region Code**: Domain region code. 'EU' or 'US' are possible values. The default is 'US'.
  - **Replication Start Date**: UTC date and time in the format 2020-10-01 00:00:00. Any data before this date will not be replicated. If omitted, defaults to 90 days ago.

## Step 2: Set up the MailGun connector in Airbyte

### For Airbyte Cloud:

1. [Log into your Airbyte Cloud](https://cloud.airbyte.com/workspaces) account.
2. In the left navigation bar, click **Sources**. In the top-right corner, click **+new source**.
3. On the Set up the source page, enter the name for the MailGun connector and select **MailGun** from the Source type dropdown.
4. Enter your api_key as `private_key`.
5. Enter the optional params configuration if needed. Supported params are: **Domain Region Code**, **Replication Start Date**.
6. Click **Set up source**.

### For Airbyte OSS:

1. Navigate to the Airbyte Open Source dashboard.
2. Set the name for your source.
3. Enter your api_key as `pivate_key`.
4. Enter the optional params configuration if needed. Supported params are: **Domain Region Code**, **Replication Start Date**.
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

<details>
  <summary>Expand to review</summary>

| Version | Date       | Pull Request                                             | Subject                                                                         |
| :------ |:-----------| :------------------------------------------------------- |:--------------------------------------------------------------------------------|
| 0.3.1   | 2024-08-16 | [44196](https://github.com/airbytehq/airbyte/pull/44196) | Bump source-declarative-manifest version   |
| 0.3.0 | 2024-08-15 | [44130](https://github.com/airbytehq/airbyte/pull/44130) | Refactor connector to manifest-only format |
| 0.2.18 | 2024-08-12 | [43923](https://github.com/airbytehq/airbyte/pull/43923) | Update dependencies |
| 0.2.17 | 2024-08-10 | [43501](https://github.com/airbytehq/airbyte/pull/43501) | Update dependencies |
| 0.2.16 | 2024-08-03 | [43098](https://github.com/airbytehq/airbyte/pull/43098) | Update dependencies |
| 0.2.15 | 2024-07-27 | [42716](https://github.com/airbytehq/airbyte/pull/42716) | Update dependencies |
| 0.2.14 | 2024-07-20 | [42241](https://github.com/airbytehq/airbyte/pull/42241) | Update dependencies |
| 0.2.13 | 2024-07-13 | [41890](https://github.com/airbytehq/airbyte/pull/41890) | Update dependencies |
| 0.2.12 | 2024-07-10 | [41582](https://github.com/airbytehq/airbyte/pull/41582) | Update dependencies |
| 0.2.11 | 2024-07-06 | [40790](https://github.com/airbytehq/airbyte/pull/40790) | Update dependencies |
| 0.2.10 | 2024-06-25 | [40491](https://github.com/airbytehq/airbyte/pull/40491) | Update dependencies |
| 0.2.9 | 2024-06-22 | [40106](https://github.com/airbytehq/airbyte/pull/40106) | Update dependencies |
| 0.2.8 | 2024-06-06 | [39229](https://github.com/airbytehq/airbyte/pull/39229) | [autopull] Upgrade base image to v1.2.2 |
| 0.2.7 | 2024-05-28 | [38176](https://github.com/airbytehq/airbyte/pull/38176) | Make connector compatible with Builder |
| 0.2.6 | 2024-05-02 | [37594](https://github.com/airbytehq/airbyte/pull/37594) | Change `last_recrods` to `last_record` |
| 0.2.5 | 2024-04-19 | [37193](https://github.com/airbytehq/airbyte/pull/37193) | Updating to 0.80.0 CDK |
| 0.2.4 | 2024-04-18 | [37193](https://github.com/airbytehq/airbyte/pull/37193) | Manage dependencies with Poetry. |
| 0.2.3 | 2024-04-15 | [37193](https://github.com/airbytehq/airbyte/pull/37193) | Base image migration: remove Dockerfile and use the python-connector-base image |
| 0.2.2 | 2024-04-12 | [37193](https://github.com/airbytehq/airbyte/pull/37193) | schema descriptions |
| 0.2.1 | 2023-10-16 | [31405](https://github.com/airbytehq/airbyte/pull/31405) | Fixed test connection failure if date field is empty |
| 0.2.0 | 2023-08-05 | [29122](https://github.com/airbytehq/airbyte/pull/29122) | Migrate to Low Code |
| 0.1.1 | 2023-02-13 | [22939](https://github.com/airbytehq/airbyte/pull/22939) | Specified date formatting in specification |
| 0.1.0 | 2021-11-09 | [8056](https://github.com/airbytehq/airbyte/pull/8056) | New Source: Mailgun |

</details>

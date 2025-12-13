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
| 0.3.42 | 2025-12-09 | [70745](https://github.com/airbytehq/airbyte/pull/70745) | Update dependencies |
| 0.3.41 | 2025-11-25 | [70116](https://github.com/airbytehq/airbyte/pull/70116) | Update dependencies |
| 0.3.40 | 2025-11-18 | [69581](https://github.com/airbytehq/airbyte/pull/69581) | Update dependencies |
| 0.3.39 | 2025-10-29 | [68972](https://github.com/airbytehq/airbyte/pull/68972) | Update dependencies |
| 0.3.38 | 2025-10-21 | [68294](https://github.com/airbytehq/airbyte/pull/68294) | Update dependencies |
| 0.3.37 | 2025-10-14 | [68046](https://github.com/airbytehq/airbyte/pull/68046) | Update dependencies |
| 0.3.36 | 2025-10-07 | [67518](https://github.com/airbytehq/airbyte/pull/67518) | Update dependencies |
| 0.3.35 | 2025-09-30 | [66817](https://github.com/airbytehq/airbyte/pull/66817) | Update dependencies |
| 0.3.34 | 2025-09-24 | [66646](https://github.com/airbytehq/airbyte/pull/66646) | Update dependencies |
| 0.3.33 | 2025-09-09 | [66043](https://github.com/airbytehq/airbyte/pull/66043) | Update dependencies |
| 0.3.32 | 2025-08-23 | [65321](https://github.com/airbytehq/airbyte/pull/65321) | Update dependencies |
| 0.3.31 | 2025-08-09 | [64607](https://github.com/airbytehq/airbyte/pull/64607) | Update dependencies |
| 0.3.30 | 2025-08-02 | [64265](https://github.com/airbytehq/airbyte/pull/64265) | Update dependencies |
| 0.3.29 | 2025-07-26 | [63915](https://github.com/airbytehq/airbyte/pull/63915) | Update dependencies |
| 0.3.28 | 2025-07-19 | [63508](https://github.com/airbytehq/airbyte/pull/63508) | Update dependencies |
| 0.3.27 | 2025-07-12 | [63109](https://github.com/airbytehq/airbyte/pull/63109) | Update dependencies |
| 0.3.26 | 2025-07-05 | [62570](https://github.com/airbytehq/airbyte/pull/62570) | Update dependencies |
| 0.3.25 | 2025-06-28 | [62198](https://github.com/airbytehq/airbyte/pull/62198) | Update dependencies |
| 0.3.24 | 2025-06-21 | [61848](https://github.com/airbytehq/airbyte/pull/61848) | Update dependencies |
| 0.3.23 | 2025-06-14 | [60725](https://github.com/airbytehq/airbyte/pull/60725) | Update dependencies |
| 0.3.22 | 2025-05-10 | [59896](https://github.com/airbytehq/airbyte/pull/59896) | Update dependencies |
| 0.3.21 | 2025-05-03 | [59251](https://github.com/airbytehq/airbyte/pull/59251) | Update dependencies |
| 0.3.20 | 2025-04-26 | [58768](https://github.com/airbytehq/airbyte/pull/58768) | Update dependencies |
| 0.3.19 | 2025-04-19 | [58183](https://github.com/airbytehq/airbyte/pull/58183) | Update dependencies |
| 0.3.18 | 2025-04-12 | [57752](https://github.com/airbytehq/airbyte/pull/57752) | Update dependencies |
| 0.3.17 | 2025-04-05 | [57029](https://github.com/airbytehq/airbyte/pull/57029) | Update dependencies |
| 0.3.16 | 2025-03-29 | [56670](https://github.com/airbytehq/airbyte/pull/56670) | Update dependencies |
| 0.3.15 | 2025-03-22 | [56078](https://github.com/airbytehq/airbyte/pull/56078) | Update dependencies |
| 0.3.14 | 2025-03-08 | [55465](https://github.com/airbytehq/airbyte/pull/55465) | Update dependencies |
| 0.3.13 | 2025-03-01 | [54810](https://github.com/airbytehq/airbyte/pull/54810) | Update dependencies |
| 0.3.12 | 2025-02-22 | [54297](https://github.com/airbytehq/airbyte/pull/54297) | Update dependencies |
| 0.3.11 | 2025-02-15 | [53823](https://github.com/airbytehq/airbyte/pull/53823) | Update dependencies |
| 0.3.10 | 2025-02-08 | [53258](https://github.com/airbytehq/airbyte/pull/53258) | Update dependencies |
| 0.3.9 | 2025-02-01 | [52786](https://github.com/airbytehq/airbyte/pull/52786) | Update dependencies |
| 0.3.8 | 2025-01-25 | [52284](https://github.com/airbytehq/airbyte/pull/52284) | Update dependencies |
| 0.3.7 | 2025-01-18 | [51815](https://github.com/airbytehq/airbyte/pull/51815) | Update dependencies |
| 0.3.6 | 2025-01-11 | [51144](https://github.com/airbytehq/airbyte/pull/51144) | Update dependencies |
| 0.3.5 | 2024-12-28 | [50592](https://github.com/airbytehq/airbyte/pull/50592) | Update dependencies |
| 0.3.4 | 2024-12-21 | [50128](https://github.com/airbytehq/airbyte/pull/50128) | Update dependencies |
| 0.3.3 | 2024-12-14 | [49613](https://github.com/airbytehq/airbyte/pull/49613) | Update dependencies |
| 0.3.2 | 2024-12-12 | [47680](https://github.com/airbytehq/airbyte/pull/47680) | Update dependencies |
| 0.3.1 | 2024-08-16 | [44196](https://github.com/airbytehq/airbyte/pull/44196) | Bump source-declarative-manifest version |
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

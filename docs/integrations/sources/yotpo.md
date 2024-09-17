# Yotpo

This page contains the setup guide and reference information for the [Yotpo](https://apidocs.yotpo.com/reference/welcome) source

## Prerequisites

Access Token (which acts as bearer token) is mandate for this connector to work, It could be generated from the auth token call (ref - https://apidocs.yotpo.com/reference/yotpo-authentication).

## Setup guide

### Step 1: Set up Yotpo connection

- Generate an Yotpo access token via auth endpoint (ref - https://apidocs.yotpo.com/reference/yotpo-authentication)
- Setup params (All params are required)
- Available params
  - access_token: The generated access token
  - app_key: Seen at the yotpo settings (ref - https://settings.yotpo.com/#/general_settings)
  - start_date: Date filter for eligible streams, enter
  - email: Registered email address

## Step 2: Set up the Yotpo connector in Airbyte

### For Airbyte Cloud:

1. [Log into your Airbyte Cloud](https://cloud.airbyte.io/workspaces) account.
2. In the left navigation bar, click **Sources**. In the top-right corner, click **+new source**.
3. On the Set up the source page, enter the name for the Yotpo connector and select **Yotpo** from the Source type dropdown.
4. Enter your `access_token, app_key, start_date and email`.
5. Click **Set up source**.

### For Airbyte OSS:

1. Navigate to the Airbyte Open Source dashboard.
2. Set the name for your source.
3. Enter your `access_token, app_key, start_date and email`.
4. Click **Set up source**.

## Supported sync modes

The Yotpo source connector supports the following [sync modes](https://docs.airbyte.com/cloud/core-concepts#connection-sync-modes):

| Feature                       | Supported? |
| :---------------------------- | :--------- |
| Full Refresh Sync             | Yes        |
| Incremental Sync              | Yes        |
| Replicate Incremental Deletes | No         |
| SSL connection                | Yes        |
| Namespaces                    | No         |

## Supported Streams

- email_analytics
- raw_data
- reviews
- unsubscribers
- webhooks
- webhook_events

## API method example

GET https://api.yotpo.com/v1/apps/APPAAAAAATTTTTTDDDDDD/reviews?utoken=abcdefghikjlimls

## Performance considerations

Yotpo [API reference](https://api.yotpo.com/v1/) has v1 at present. The connector as default uses v1 and changed according to different endpoints.

## Changelog

<details>
  <summary>Expand to review</summary>

| Version | Date       | Pull Request                                            | Subject        |
| :------ | :--------- | :------------------------------------------------------ | :------------- |
| 0.2.0 | 2024-08-26 | [44780](https://github.com/airbytehq/airbyte/pull/44780) | Refactor connector to manifest-only format |
| 0.1.14 | 2024-08-24 | [44661](https://github.com/airbytehq/airbyte/pull/44661) | Update dependencies |
| 0.1.13 | 2024-08-17 | [44254](https://github.com/airbytehq/airbyte/pull/44254) | Update dependencies |
| 0.1.12 | 2024-08-12 | [43891](https://github.com/airbytehq/airbyte/pull/43891) | Update dependencies |
| 0.1.11 | 2024-08-10 | [43658](https://github.com/airbytehq/airbyte/pull/43658) | Update dependencies |
| 0.1.10 | 2024-08-03 | [43198](https://github.com/airbytehq/airbyte/pull/43198) | Update dependencies |
| 0.1.9 | 2024-07-27 | [42610](https://github.com/airbytehq/airbyte/pull/42610) | Update dependencies |
| 0.1.8 | 2024-07-20 | [42275](https://github.com/airbytehq/airbyte/pull/42275) | Update dependencies |
| 0.1.7 | 2024-07-13 | [41815](https://github.com/airbytehq/airbyte/pull/41815) | Update dependencies |
| 0.1.6 | 2024-07-10 | [41444](https://github.com/airbytehq/airbyte/pull/41444) | Update dependencies |
| 0.1.5 | 2024-07-09 | [41250](https://github.com/airbytehq/airbyte/pull/41250) | Update dependencies |
| 0.1.4 | 2024-07-06 | [40795](https://github.com/airbytehq/airbyte/pull/40795) | Update dependencies |
| 0.1.3 | 2024-06-25 | [40488](https://github.com/airbytehq/airbyte/pull/40488) | Update dependencies |
| 0.1.2 | 2024-06-21 | [39945](https://github.com/airbytehq/airbyte/pull/39945) | Update dependencies |
| 0.1.1 | 2024-05-20 | [38390](https://github.com/airbytehq/airbyte/pull/38390) | [autopull] base image + poetry + up_to_date |
| 0.1.0   | 2023-04-14 | [Init](https://github.com/airbytehq/airbyte/pull/25532) | Initial commit |

</details>

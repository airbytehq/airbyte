# Yandex Metrica

This page contains the setup guide and reference information for the Yandex Metrica source connector.

## Prerequisites

- Counter ID
- OAuth2 Token

## Setup guide

### Step 1: Set up Yandex Metrica

1. [Create Yandex Metrica account](https://metrica.yandex.com/) if you don't already have one.
2. Head to [Management page](https://metrica.yandex.com/list) and add new tag or choose an existing one.
3. At the top of the dashboard you will see 8 digit number to the right of your website name. This is your **Counter ID**.
4. Create a new app or choose an existing one from [My apps page](https://oauth.yandex.com/).
   - Which platform is the app required for?: **Web services**
   - Callback URL: https://oauth.yandex.com/verification_code
   - What data do you need?: **Yandex.Metrica**. Read permission will suffice.
5. Choose your app from [the list](https://oauth.yandex.com/).
   - To create your API key you will need to grab your **ClientID**,
   - Now to get the API key craft a GET request to an endpoint *https://oauth.yandex.com/authorizE?response_type=token&client_id=YOUR_CLIENT_ID*
   - You will receive a response with your **API key**. Save it.

### Step 2: Set up the Yandex Metrica connector in Airbyte

1. [Log into your Airbyte Cloud](https://cloud.airbyte.io/workspaces) account.
2. Click **Sources** and then click **+ New source**.
3. On the Set up the source page, select **Yandex Metrica** from the **Source type** dropdown.
4. Enter a name for the Yandex Metrica connector.
5. Enter Authentication Token from step 1.
6. Enter Counter ID.
7. Enter the Start Date in format `YYYY-MM-DD`.
8. Enter the End Date in format `YYYY-MM-DD` (Optional).

#### For Airbyte Open Source:

1. Navigate to the Airbyte Open Source dashboard.
2. Click **Sources** and then click **+ New source**.
3. On the Set up the source page, select **Yandex Metrica** from the Source type dropdown.
4. Enter the name for the Yandex Metrica connector.
5. Enter Authentication Token from step 1.
6. Enter Counter ID.
7. Enter the Start Date in format `YYYY-MM-DD`.
8. Enter the End Date in format `YYYY-MM-DD` (Optional).

## Supported sync modes

The Yandex Metrica source connector supports the following [sync modes](https://docs.airbyte.com/cloud/core-concepts#connection-sync-modes):

- [Full Refresh - Overwrite](https://docs.airbyte.com/understanding-airbyte/connections/full-refresh-overwrite/)
- [Full Refresh - Append](https://docs.airbyte.com/understanding-airbyte/connections/full-refresh-append)
- [Incremental - Append](https://docs.airbyte.com/understanding-airbyte/connections/incremental-append)
- [Incremental - Append + Deduped](https://docs.airbyte.com/understanding-airbyte/connections/incremental-append-deduped)

## Supported Streams

- [Views](https://yandex.com/dev/metrika/doc/api2/logs/fields/hits.html) \(Incremental\).
- [Sessions](https://yandex.com/dev/metrika/doc/api2/logs/fields/visits.html) \(Incremental\).

## Performance considerations

Yandex Metrica has some [rate limits](https://yandex.ru/dev/metrika/doc/api2/intro/quotas.html)

:::tip

It is recommended to sync data once a day.

:::

:::note

Because of the way API works some syncs may take a long time to finish. Timeout period is 2 hours.

:::

## Data type mapping

| Integration Type | Airbyte Type | Notes |
| :--------------- | :----------- | :---- |
| `string`         | `string`     |       |
| `integer`        | `integer`    |       |
| `number`         | `number`     |       |
| `array`          | `array`      |       |
| `object`         | `object`     |       |

## Changelog

<details>
  <summary>Expand to review</summary>

| Version | Date       | Pull Request                                             | Subject                                                                         |
| :------ | :--------- | :------------------------------------------------------- | :------------------------------------------------------------------------------ |
| 1.0.21 | 2024-10-12 | [46836](https://github.com/airbytehq/airbyte/pull/46836) | Update dependencies |
| 1.0.20 | 2024-10-05 | [46444](https://github.com/airbytehq/airbyte/pull/46444) | Update dependencies |
| 1.0.19 | 2024-09-28 | [46161](https://github.com/airbytehq/airbyte/pull/46161) | Update dependencies |
| 1.0.18 | 2024-09-21 | [45755](https://github.com/airbytehq/airbyte/pull/45755) | Update dependencies |
| 1.0.17 | 2024-09-14 | [45536](https://github.com/airbytehq/airbyte/pull/45536) | Update dependencies |
| 1.0.16 | 2024-09-07 | [45315](https://github.com/airbytehq/airbyte/pull/45315) | Update dependencies |
| 1.0.15 | 2024-08-31 | [44702](https://github.com/airbytehq/airbyte/pull/44702) | Update dependencies |
| 1.0.14 | 2024-08-17 | [44291](https://github.com/airbytehq/airbyte/pull/44291) | Update dependencies |
| 1.0.13 | 2024-08-10 | [43693](https://github.com/airbytehq/airbyte/pull/43693) | Update dependencies |
| 1.0.12 | 2024-08-03 | [43072](https://github.com/airbytehq/airbyte/pull/43072) | Update dependencies |
| 1.0.11 | 2024-07-27 | [42172](https://github.com/airbytehq/airbyte/pull/42172) | Update dependencies |
| 1.0.10 | 2024-07-13 | [41925](https://github.com/airbytehq/airbyte/pull/41925) | Update dependencies |
| 1.0.9 | 2024-07-10 | [41431](https://github.com/airbytehq/airbyte/pull/41431) | Update dependencies |
| 1.0.8 | 2024-07-09 | [40837](https://github.com/airbytehq/airbyte/pull/40837) | Update dependencies |
| 1.0.7 | 2024-06-25 | [40368](https://github.com/airbytehq/airbyte/pull/40368) | Update dependencies |
| 1.0.6 | 2024-06-21 | [39934](https://github.com/airbytehq/airbyte/pull/39934) | Update dependencies |
| 1.0.5 | 2024-06-04 | [38999](https://github.com/airbytehq/airbyte/pull/38999) | [autopull] Upgrade base image to v1.2.1 |
| 1.0.4 | 2024-04-19 | [37296](https://github.com/airbytehq/airbyte/pull/37296) | Updating to 0.80.0 CDK |
| 1.0.3 | 2024-04-18 | [37296](https://github.com/airbytehq/airbyte/pull/37296) | Manage dependencies with Poetry. |
| 1.0.2 | 2024-04-15 | [37296](https://github.com/airbytehq/airbyte/pull/37296) | Base image migration: remove Dockerfile and use the python-connector-base image |
| 1.0.1 | 2024-04-12 | [37296](https://github.com/airbytehq/airbyte/pull/37296) | schema descriptions |
| 1.0.0 | 2023-03-20 | [24188](https://github.com/airbytehq/airbyte/pull/24188) | Migrate to Beta; Change state structure |
| 0.1.0 | 2022-09-09 | [15061](https://github.com/airbytehq/airbyte/pull/15061) | 🎉 New Source: Yandex metrica |

</details>

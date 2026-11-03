# Aircall

This page contains the setup guide and reference information for the [Aircall](https://developer.aircall.io/api-references/#rest-api) source

## Prerequisites

The connector supports two authentication methods:

- **OAuth 2.0** (default): an Aircall Admin authorizes Airbyte's Aircall app. This requires Airbyte's Aircall Technology Partner app, which is not yet available in Airbyte Cloud. Self-managed deployments need their own Aircall partner app's client ID and client secret.
- **API Key**: an Aircall Admin creates an API key in the Aircall Dashboard under **Integrations & API > API Keys**. The API ID and API token are both required.

## Setup guide

### Step 1: Set up Aircall connection

- Choose an authentication method. For **API Key**, create an API key in **Integrations & API > API Keys** in the Aircall Dashboard. `start_date` is retained for compatibility but is unused.
- Available params
  - `credentials`: The authentication method.
    - **OAuth 2.0**: `client_id` and `client_secret` of the Aircall partner app, and the `access_token` Aircall returns when an Admin installs the app. Aircall access tokens do not expire.
    - **API Key**: `api_id`, your Aircall API ID, and `api_token`, the API token shown with the API ID.
  - `start_date`: Unused since 0.5.0. Calls start at 186 days before the sync; other streams read every record.
  - `window_in_days`: Optional number of days per API request for calls and contacts. Defaults to 1 day for calls and 30 days for contacts; reduce it if a window exceeds Aircall's 10,000-result limit.
  - `num_workers`: Optional concurrent workers, from 1 to 4 (default 2). Workers share Aircall's company-wide rate limit of 120 requests per minute.

### Step 2: Set up the Aircall connector in Airbyte

#### For Airbyte Cloud:

1. [Log into your Airbyte Cloud](https://cloud.airbyte.io/workspaces) account.
2. In the left navigation bar, click **Sources**. In the top-right corner, click **+new source**.
3. On the Set up the source page, enter the name for the Aircall connector and select **Aircall** from the Source type dropdown.
4. Under **Authentication**, select **OAuth 2.0** and click **Authenticate your Aircall account**, or select **API Key** and enter your API ID and API token. `start_date` is optional and unused.
5. Click **Set up source**.

#### For Airbyte OSS:

1. Navigate to the Airbyte Open Source dashboard.
2. Set the name for your source.
3. Under **Authentication**, select **API Key** and enter your API ID and API token, or select **OAuth 2.0** and enter your partner app's client ID, client secret and access token. `start_date` is optional and unused.
4. Click **Set up source**.

## Supported sync modes

The Aircall source connector supports the following [sync modes](https://docs.airbyte.com/cloud/core-concepts#connection-sync-modes):

| Feature                       | Supported? |
| :---------------------------- | :--------- |
| Full Refresh Sync             | Yes        |
| Incremental Sync              | Yes        |
| Replicate Incremental Deletes | No         |
| SSL connection                | Yes        |
| Namespaces                    | No         |

## Supported Streams

| Stream            | Sync mode                 | Notes                                                         |
| :---------------- | :------------------------ | :------------------------------------------------------------ |
| calls             | Full refresh, incremental | Incremental calls use `started_at` with a three-day lookback. |
| company           | Full refresh              | Used for connection checks.                                   |
| contacts          | Full refresh              |                                                               |
| numbers           | Full refresh, incremental | Incremental sync rereads all records to capture edits.        |
| tags              | Full refresh              |                                                               |
| user_availability | Full refresh              |                                                               |
| users             | Full refresh              | Uses the Aircall User V2 API.                                 |
| teams             | Full refresh, incremental | Incremental sync rereads all records to capture edits.        |
| webhooks          | Full refresh              |                                                               |

## API method example

GET https://api.aircall.io/v1/numbers

## Performance considerations

The connector uses Aircall's [v1 API](https://developer.aircall.io/api-references/). Calls and contacts requests are split into configurable date windows to stay below Aircall's 10,000-result cap. Aircall's 120-requests-per-minute limit applies company-wide.

## IP allow list

If you use Airbyte Cloud and your organization restricts access to specific IPs, add the [Airbyte Cloud IP addresses](https://docs.airbyte.com/platform/operating-airbyte/ip-allowlist) to your allow list.

## Changelog

<details>
  <summary>Expand to review</summary>

| Version | Date       | Pull Request                                                                   | Subject                     |
| :------ | :--------- | :----------------------------------------------------------------------------- | :-------------------------- |
| 0.7.0 | 2026-11-03 | [PRNUM](https://github.com/airbytehq/airbyte/pull/PRNUM) | Add OAuth 2.0 authentication as the default; existing API key configurations move to the API Key option automatically |
| 0.5.0 | 2026-11-03 | [90835](https://github.com/airbytehq/airbyte/pull/90835) | Add incremental sync for calls, rate-limit handling and request windows that avoid Aircall's 10,000-result limit |
| 0.4.27 | 2026-10-13 | [88524](https://github.com/airbytehq/airbyte/pull/88524) | Update dependencies |
| 0.4.26 | 2026-10-06 | [87742](https://github.com/airbytehq/airbyte/pull/87742) | Update dependencies |
| 0.4.25 | 2026-09-29 | [87057](https://github.com/airbytehq/airbyte/pull/87057) | Update dependencies |
| 0.4.24 | 2026-09-23 | [85909](https://github.com/airbytehq/airbyte/pull/85909) | Migrate the `users` stream to the Aircall User V2 API ahead of the V1 sunset and add pagination |
| 0.4.23 | 2026-09-22 | [86517](https://github.com/airbytehq/airbyte/pull/86517) | Update dependencies |
| 0.4.22 | 2026-09-15 | [85956](https://github.com/airbytehq/airbyte/pull/85956) | Update dependencies |
| 0.4.21 | 2026-09-08 | [85381](https://github.com/airbytehq/airbyte/pull/85381) | Update dependencies |
| 0.4.20 | 2026-08-18 | [84505](https://github.com/airbytehq/airbyte/pull/84505) | Update dependencies |
| 0.4.19 | 2026-08-11 | [83832](https://github.com/airbytehq/airbyte/pull/83832) | Update dependencies |
| 0.4.18 | 2026-08-04 | [83374](https://github.com/airbytehq/airbyte/pull/83374) | Update dependencies |
| 0.4.17 | 2026-07-28 | [82810](https://github.com/airbytehq/airbyte/pull/82810) | Update dependencies |
| 0.4.16 | 2026-07-21 | [82307](https://github.com/airbytehq/airbyte/pull/82307) | Update dependencies |
| 0.4.15 | 2026-07-14 | [81718](https://github.com/airbytehq/airbyte/pull/81718) | Update dependencies |
| 0.4.14 | 2026-06-30 | [80992](https://github.com/airbytehq/airbyte/pull/80992) | Update dependencies |
| 0.4.13 | 2026-06-23 | [80364](https://github.com/airbytehq/airbyte/pull/80364) | Update dependencies |
| 0.4.12 | 2026-06-16 | [79750](https://github.com/airbytehq/airbyte/pull/79750) | Update dependencies |
| 0.4.11 | 2026-06-09 | [79207](https://github.com/airbytehq/airbyte/pull/79207) | Update dependencies |
| 0.4.10 | 2026-06-02 | [78574](https://github.com/airbytehq/airbyte/pull/78574) | Update dependencies |
| 0.4.9 | 2026-04-28 | [77183](https://github.com/airbytehq/airbyte/pull/77183) | Update dependencies |
| 0.4.8 | 2026-04-21 | [76490](https://github.com/airbytehq/airbyte/pull/76490) | Update dependencies |
| 0.4.7 | 2026-03-17 | [74979](https://github.com/airbytehq/airbyte/pull/74979) | Update dependencies |
| 0.4.6 | 2026-02-10 | [73001](https://github.com/airbytehq/airbyte/pull/73001) | Update dependencies |
| 0.4.5 | 2026-01-27 | [72373](https://github.com/airbytehq/airbyte/pull/72373) | Update dependencies |
| 0.4.4 | 2026-01-14 | [71503](https://github.com/airbytehq/airbyte/pull/71503) | Update dependencies |
| 0.4.3 | 2025-12-02 | [70282](https://github.com/airbytehq/airbyte/pull/70282) | Update dependencies |
| 0.4.2 | 2025-10-29 | [65055](https://github.com/airbytehq/airbyte/pull/65055) | Update dependencies |
| 0.4.1 | 2025-09-12 | [66197](https://github.com/airbytehq/airbyte/pull/66197) | Update to CDK v7 |
| 0.4.0 | 2024-08-23 | [44597](https://github.com/airbytehq/airbyte/pull/44597) | Refactor connector to manifest-only format |
| 0.3.0 | 2024-08-19 | [44437](https://github.com/airbytehq/airbyte/pull/44437) | Fix pagination |
| 0.2.12 | 2024-08-17 | [43879](https://github.com/airbytehq/airbyte/pull/43879) | Update dependencies |
| 0.2.11 | 2024-08-10 | [43482](https://github.com/airbytehq/airbyte/pull/43482) | Update dependencies |
| 0.2.10 | 2024-08-03 | [43101](https://github.com/airbytehq/airbyte/pull/43101) | Update dependencies |
| 0.2.9 | 2024-07-27 | [42743](https://github.com/airbytehq/airbyte/pull/42743) | Update dependencies |
| 0.2.8 | 2024-07-20 | [42357](https://github.com/airbytehq/airbyte/pull/42357) | Update dependencies |
| 0.2.7 | 2024-07-13 | [41708](https://github.com/airbytehq/airbyte/pull/41708) | Update dependencies |
| 0.2.6 | 2024-07-10 | [41448](https://github.com/airbytehq/airbyte/pull/41448) | Update dependencies |
| 0.2.5 | 2024-07-09 | [41156](https://github.com/airbytehq/airbyte/pull/41156) | Update dependencies |
| 0.2.4 | 2024-07-06 | [40801](https://github.com/airbytehq/airbyte/pull/40801) | Update dependencies |
| 0.2.3 | 2024-06-25 | [40503](https://github.com/airbytehq/airbyte/pull/40503) | Update dependencies |
| 0.2.2 | 2024-06-21 | [39920](https://github.com/airbytehq/airbyte/pull/39920) | Update dependencies |
| 0.2.2 | 2024-06-20 | [39681](https://github.com/airbytehq/airbyte/pull/39681) | Update dependencies |
| 0.2.1 | 2024-06-06 | [38454](https://github.com/airbytehq/airbyte/pull/38454) | [autopull] base image + poetry + up_to_date |
| 0.2.0   | 2023-06-20 | [Correcting availablity typo](https://github.com/airbytehq/airbyte/pull/27433) | Correcting availablity typo |
| 0.1.0   | 2023-04-19 | [Init](https://github.com/airbytehq/airbyte/pull/)                             | Initial commit              |

</details>

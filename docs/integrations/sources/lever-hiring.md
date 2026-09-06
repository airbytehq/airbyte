# Lever Hiring

This page guides you through setting up the Lever Hiring source connector. The connector reads recruiting data from the [Lever API](https://hire.lever.co/developer/documentation).

## Prerequisites

- A Lever account
- One of the following credentials:
  - **API key** (recommended for most users): Create one in Lever under **Settings** > **Integrations and API** > **API Credentials**. Lever notes that API keys are intended for internal workflows and carry broad privileges, so store the key securely.
  - **OAuth client ID, client secret, and refresh token**: Lever offers OAuth only to registered partner applications through its [partner program](https://hire.lever.co/developer/documentation#oauth). If you use Airbyte Cloud, you can authenticate through the Airbyte-managed OAuth flow without creating your own app.
- Whether your Lever account is a **Production** or **Sandbox** environment. The connector calls `api.lever.co` for production and `api.sandbox.lever.co` for sandbox.

## Setup guide

1. In the Airbyte UI, select **Sources** and then **New source**.
2. Search for and select **Lever Hiring**.
3. Enter a **Source name**.
4. For **Start Date**, enter a UTC timestamp in the format `YYYY-MM-DDTHH:MM:SSZ`, for example `2021-03-01T00:00:00Z`. The connector passes this value as the `updated_at_start` request parameter when it lists opportunities. Opportunities last updated before this date, and their related applications, interviews, notes, offers, and referrals, aren't replicated. It has no effect on the `users` stream.
5. For **Environment**, select **Production** or **Sandbox**. The default is **Sandbox**, so change it to **Production** if you connect to a regular Lever account.
6. For **Authentication Mechanism**, choose one of the following:
   - **Authenticate via Lever (Api Key)**: Enter your Lever API key.
   - **Authenticate via Lever (OAuth)**: On Airbyte Cloud, use the OAuth button to sign in to Lever and grant access. On self-managed Airbyte, enter the **Client ID**, **Client Secret**, and **Refresh Token** for your registered Lever OAuth app. The refresh token must have been issued with the `offline_access` scope.
7. Select **Set up source**.

The connector verifies your credentials by requesting the `users` endpoint.

## Supported sync modes

| Feature                   | Supported? |
| :------------------------ | :--------- |
| Full Refresh Sync         | Yes        |
| Incremental - Append Sync | Yes (`opportunities` only) |
| Namespaces                | No         |

## Supported streams

| Stream | Lever endpoint | Sync modes | Notes |
| :----- | :------------- | :--------- | :---- |
| [Opportunities](https://hire.lever.co/developer/documentation#list-all-opportunities) | `GET /opportunities` | Full Refresh, Incremental | Incremental syncs use the `updatedAt` field as the cursor and request 30-day windows with `updated_at_start` and `updated_at_end`. |
| [Users](https://hire.lever.co/developer/documentation#list-all-users) | `GET /users` | Full Refresh | Includes deactivated users (`includeDeactivated=true`). Not filtered by **Start Date**. |
| [Applications](https://hire.lever.co/developer/documentation#list-all-applications) | `GET /opportunities/{id}/applications` | Full Refresh | Fetched per opportunity. |
| [Interviews](https://hire.lever.co/developer/documentation#list-all-interviews) | `GET /opportunities/{id}/interviews` | Full Refresh | Fetched per opportunity. |
| [Notes](https://hire.lever.co/developer/documentation#list-all-notes) | `GET /opportunities/{id}/notes` | Full Refresh | Fetched per opportunity. |
| [Offers](https://hire.lever.co/developer/documentation#list-all-offers) | `GET /opportunities/{id}/offers` | Full Refresh | Fetched per opportunity. |
| [Referrals](https://hire.lever.co/developer/documentation#list-all-referrals) | `GET /opportunities/{id}/referrals` | Full Refresh | Fetched per opportunity. |

The applications, interviews, notes, offers, and referrals streams first list opportunities using the same `updated_at_start`/`updated_at_end` windows as the opportunities stream, starting from your **Start Date**, then request the child records for each opportunity. Records belonging to opportunities outside that window aren't synced. Because each opportunity requires one request per child stream, syncing these streams for a large Lever account can take a long time.

Lever's [`updated_at_start` filter](https://hire.lever.co/developer/documentation#list-all-opportunities) matches any change to an opportunity, while the `updatedAt` field the connector uses as its cursor only reflects changes to a specific set of opportunity fields. Keep this in mind if incremental syncs return opportunities you didn't expect, or miss changes you did.

## Limitations and troubleshooting

### Rate limits

Lever rate limits requests per API key using a token bucket: a steady state of 10 requests per second, with bursts up to 20 requests per second. There are no endpoint-specific limits. The connector retries requests that Lever rejects with `429 Too Many Requests`. See [Lever rate limits](https://hire.lever.co/developer/documentation#rate-limiting).

### Incremental syncs stuck on the same records

Versions before 0.4.42 used a cursor granularity that didn't match the millisecond timestamps Lever returns, which could cause incremental syncs of the `opportunities` stream to repeatedly re-request the same window. Upgrade to 0.4.42 or later to resolve this.

### IP allow list

If you use Airbyte Cloud and your organization restricts access to specific IPs, add the [Airbyte Cloud IP addresses](https://docs.airbyte.com/platform/operating-airbyte/ip-allowlist) to your allow list.

## Changelog

<details>
  <summary>Expand to review</summary>

| Version | Date       | Pull Request                                             | Subject                           |
|:--------|:-----------|:---------------------------------------------------------|:----------------------------------|
| 0.4.42 | 2026-09-03 | [80293](https://github.com/airbytehq/airbyte/pull/80293) | Fix incremental cursor stuck by aligning cursor_granularity with millisecond datetime_format |
| 0.4.41 | 2026-08-18 | [84669](https://github.com/airbytehq/airbyte/pull/84669) | Update dependencies |
| 0.4.40 | 2026-08-11 | [84028](https://github.com/airbytehq/airbyte/pull/84028) | Update dependencies |
| 0.4.39 | 2026-08-04 | [83535](https://github.com/airbytehq/airbyte/pull/83535) | Update dependencies |
| 0.4.38 | 2026-07-28 | [83011](https://github.com/airbytehq/airbyte/pull/83011) | Update dependencies |
| 0.4.37 | 2026-07-21 | [82510](https://github.com/airbytehq/airbyte/pull/82510) | Update dependencies |
| 0.4.36 | 2026-07-14 | [81920](https://github.com/airbytehq/airbyte/pull/81920) | Update dependencies |
| 0.4.35 | 2026-06-30 | [81138](https://github.com/airbytehq/airbyte/pull/81138) | Update dependencies |
| 0.4.34 | 2026-06-23 | [80552](https://github.com/airbytehq/airbyte/pull/80552) | Update dependencies |
| 0.4.33 | 2026-06-16 | [79956](https://github.com/airbytehq/airbyte/pull/79956) | Update dependencies |
| 0.4.32 | 2026-06-09 | [79384](https://github.com/airbytehq/airbyte/pull/79384) | Update dependencies |
| 0.4.31 | 2026-06-02 | [78801](https://github.com/airbytehq/airbyte/pull/78801) | Update dependencies |
| 0.4.30 | 2026-04-28 | [77295](https://github.com/airbytehq/airbyte/pull/77295) | Update dependencies |
| 0.4.29 | 2026-04-21 | [76653](https://github.com/airbytehq/airbyte/pull/76653) | Update dependencies |
| 0.4.28 | 2026-03-31 | [75032](https://github.com/airbytehq/airbyte/pull/75032) | Update dependencies |
| 0.4.27 | 2026-02-24 | [73939](https://github.com/airbytehq/airbyte/pull/73939) | Update dependencies |
| 0.4.26 | 2026-02-17 | [73554](https://github.com/airbytehq/airbyte/pull/73554) | Update dependencies |
| 0.4.25 | 2026-02-10 | [73047](https://github.com/airbytehq/airbyte/pull/73047) | Update dependencies |
| 0.4.24 | 2026-02-03 | [72762](https://github.com/airbytehq/airbyte/pull/72762) | Update dependencies |
| 0.4.23 | 2026-01-20 | [72002](https://github.com/airbytehq/airbyte/pull/72002) | Update dependencies |
| 0.4.22 | 2026-01-14 | [71449](https://github.com/airbytehq/airbyte/pull/71449) | Update dependencies |
| 0.4.21 | 2025-12-18 | [70794](https://github.com/airbytehq/airbyte/pull/70794) | Update dependencies |
| 0.4.20 | 2025-11-25 | [69501](https://github.com/airbytehq/airbyte/pull/69501) | Update dependencies |
| 0.4.19 | 2025-10-29 | [68936](https://github.com/airbytehq/airbyte/pull/68936) | Update dependencies |
| 0.4.18 | 2025-10-21 | [68331](https://github.com/airbytehq/airbyte/pull/68331) | Update dependencies |
| 0.4.17 | 2025-10-14 | [68064](https://github.com/airbytehq/airbyte/pull/68064) | Update dependencies |
| 0.4.16 | 2025-10-07 | [67526](https://github.com/airbytehq/airbyte/pull/67526) | Update dependencies |
| 0.4.15 | 2025-09-30 | [66814](https://github.com/airbytehq/airbyte/pull/66814) | Update dependencies |
| 0.4.14 | 2025-09-24 | [66648](https://github.com/airbytehq/airbyte/pull/66648) | Update dependencies |
| 0.4.13 | 2025-09-09 | [66083](https://github.com/airbytehq/airbyte/pull/66083) | Update dependencies |
| 0.4.12 | 2025-08-23 | [65324](https://github.com/airbytehq/airbyte/pull/65324) | Update dependencies |
| 0.4.11 | 2025-08-09 | [64602](https://github.com/airbytehq/airbyte/pull/64602) | Update dependencies |
| 0.4.10 | 2025-08-02 | [64302](https://github.com/airbytehq/airbyte/pull/64302) | Update dependencies |
| 0.4.9 | 2025-07-26 | [63847](https://github.com/airbytehq/airbyte/pull/63847) | Update dependencies |
| 0.4.8 | 2025-07-19 | [63519](https://github.com/airbytehq/airbyte/pull/63519) | Update dependencies |
| 0.4.7 | 2025-07-12 | [63111](https://github.com/airbytehq/airbyte/pull/63111) | Update dependencies |
| 0.4.6 | 2025-07-05 | [62598](https://github.com/airbytehq/airbyte/pull/62598) | Update dependencies |
| 0.4.5 | 2025-06-28 | [62189](https://github.com/airbytehq/airbyte/pull/62189) | Update dependencies |
| 0.4.4 | 2025-06-21 | [61808](https://github.com/airbytehq/airbyte/pull/61808) | Update dependencies |
| 0.4.3 | 2025-06-14 | [48264](https://github.com/airbytehq/airbyte/pull/48264) | Update dependencies |
| 0.4.2 | 2024-10-28 | [43750](https://github.com/airbytehq/airbyte/pull/43750) | Update dependencies |
| 0.4.1 | 2024-08-16 | [44196](https://github.com/airbytehq/airbyte/pull/44196) | Bump source-declarative-manifest version |
| 0.4.0 | 2024-08-15 | [44133](https://github.com/airbytehq/airbyte/pull/44133) | Refactor connector to manifest-only format |
| 0.3.1 | 2024-06-04 | [39082](https://github.com/airbytehq/airbyte/pull/39082) | [autopull] Upgrade base image to v1.2.1 |
| 0.3.0 | 2024-05-08 | [36262](https://github.com/airbytehq/airbyte/pull/36262) | Migrate to Low Code |
| 0.2.0 | 2023-05-25 | [26564](https://github.com/airbytehq/airbyte/pull/26564) | Migrate to advancedAuth |
| 0.1.3 | 2022-10-14 | [17996](https://github.com/airbytehq/airbyte/pull/17996) | Add Basic Auth management |
| 0.1.2 | 2021-12-30 | [9214](https://github.com/airbytehq/airbyte/pull/9214) | Update title and descriptions |
| 0.1.1 | 2021-12-16 | [7677](https://github.com/airbytehq/airbyte/pull/7677) | OAuth Automated Authentication |
| 0.1.0 | 2021-09-22 | [6141](https://github.com/airbytehq/airbyte/pull/6141) | Add Lever Hiring Source Connector |

</details>

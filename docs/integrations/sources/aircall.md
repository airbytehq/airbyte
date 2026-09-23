# Aircall

This page contains the setup guide and reference information for the [Aircall](https://developer.aircall.io/api-references/#rest-api) source connector.

## Prerequisites

- An Aircall account. You need admin access to the Aircall Dashboard to create API keys.
- An Aircall API key. Each key consists of an **API ID** and an **API token**. The connector authenticates with [HTTP Basic authentication](https://developer.aircall.io/api-references/#basic-auth-aircall-customers), using the API ID as the username and the API token as the password.

## Setup guide

### Step 1: Create an Aircall API key

1. Log in to the [Aircall Dashboard](https://dashboard.aircall.io/) as an admin.
2. Go to **Integrations & API** > [**API Keys**](https://dashboard.aircall.io/integrations/api-keys).
3. Click **Add a new API key**.
4. Copy the **API ID** and **API token**. Aircall doesn't store the token in plain text, so you can't view it again later. If you lose it, create a new key.

### Step 2: Set up the Aircall connector in Airbyte

1. In the Airbyte UI, click **Sources** in the left navigation bar, then click **New source**.
2. Select **Aircall** from the list of sources.
3. Enter a name for the source.
4. Enter your **API ID** and **API Token**.
5. For **Date-From Filter**, enter the earliest `created_at` timestamp to sync, in the format `YYYY-MM-DDTHH:mm:ss.SSSZ` (for example, `2022-03-01T00:00:00.000Z`). This filter only applies to the `numbers` and `teams` streams. All other streams ignore it and return all records.
6. Click **Set up source**.

## Supported sync modes

The Aircall source connector supports the following [sync modes](https://docs.airbyte.com/platform/using-airbyte/core-concepts/sync-modes/):

| Feature                       | Supported? |
| :---------------------------- | :--------- |
| Full Refresh Sync             | Yes        |
| Incremental Sync              | Yes        |
| Replicate Incremental Deletes | No         |
| SSL connection                | Yes        |
| Namespaces                    | No         |

## Supported streams

| Stream              | Aircall endpoint                | Incremental | Notes                                                                                                              |
| :------------------ | :------------------------------ | :---------- | :----------------------------------------------------------------------------------------------------------------- |
| `calls`             | `GET /v1/calls`                 | No          | Aircall returns at most 10,000 calls through this endpoint, even with pagination.                                  |
| `company`           | `GET /v1/company`               | No          | Returns a single record describing your Aircall company.                                                           |
| `contacts`          | `GET /v1/contacts`              | No          | Returns shared contacts only. Aircall returns at most 10,000 contacts through this endpoint, even with pagination. |
| `numbers`           | `GET /v1/numbers`               | Yes         | Cursor field is `created_at`. Filtered by **Date-From Filter**.                                                    |
| `tags`              | `GET /v1/tags`                  | No          |                                                                                                                    |
| `teams`             | `GET /v1/teams`                 | Yes         | Cursor field is `created_at`. Filtered by **Date-From Filter**.                                                    |
| `user_availability` | `GET /v1/users/availabilities`  | No          | Returns the current availability of each user.                                                                     |
| `users`             | `GET /v2/users`                 | No          | Uses the Aircall User V2 API. See [Users stream](#users-stream).                                                   |
| `webhooks`          | `GET /v1/webhooks`              | No          |                                                                                                                    |

Incremental streams use a 31-day lookback window, so each incremental sync re-reads records created in the 31 days before the last saved cursor value.

### Users stream

Starting with connector version 0.4.24, the `users` stream reads from the [Aircall User V2 API](https://developer.aircall.io/api-references/#user-v2-overview) instead of User V1, which Aircall is deprecating on September 30, 2026. The stream's fields are unchanged, with one exception: `direct_link` values now point to `/v2/users/{id}` instead of `/v1/users/{id}`. The V2 API doesn't return a `numbers` object on user records, but the connector never synced that object, so no columns are removed. No reset is required.

Version 0.4.24 also added pagination to the `users` stream. Earlier versions returned only the first page of 20 users that Aircall returns by default. If your account has more than 20 users, the first sync after upgrading includes the users that were previously missing.

The `user_availability` stream still uses the V1 `/users/availabilities` endpoint, which isn't part of Aircall's User V1 deprecation.

## Performance considerations

Aircall limits the Public API to [120 requests per minute per company](https://developer.aircall.io/api-references/#rate-limiting). This limit is shared across all API keys and integrations in your Aircall account. The connector requests 50 records per page to reduce the number of calls it makes. If you have other integrations that use the Aircall API heavily, you may hit this limit during large syncs.

## IP allow list

If you use Airbyte Cloud and your organization restricts access to specific IPs, add the [Airbyte Cloud IP addresses](https://docs.airbyte.com/platform/operating-airbyte/ip-allowlist) to your allow list.

## Changelog

<details>
  <summary>Expand to review</summary>

| Version | Date       | Pull Request                                                                   | Subject                     |
| :------ | :--------- | :----------------------------------------------------------------------------- | :-------------------------- |
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

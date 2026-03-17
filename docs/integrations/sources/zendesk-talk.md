# Zendesk Talk

<HideInUI>

This page contains the setup guide and reference information for the [Zendesk Talk](https://www.zendesk.com/service/voice/) source connector.

</HideInUI>

## Prerequisites

- A Zendesk account with [Zendesk Talk](https://www.zendesk.com/service/voice/) enabled
- Your Zendesk subdomain (found in your account URL: `https://YOUR_SUBDOMAIN.zendesk.com`)
- One of the following authentication methods:
  - **OAuth2.0** (recommended for Airbyte Cloud): Requires a Zendesk OAuth client with `read` scope
  - **API Token**: Requires a Zendesk API token and the email address associated with the token

## Setup guide

### Step 1: Set up Zendesk Talk

Choose one of the following authentication methods:

#### Option A: API Token (recommended for Airbyte Open Source)

1. In Zendesk, go to **Admin Center** > **Apps and integrations** > **APIs** > **Zendesk API**.
2. Enable **Token Access**.
3. Click **Add API token**, give it a description, and copy the token value.

For more details, see [Generating a new API token](https://support.zendesk.com/hc/en-us/articles/226022787-Generating-a-new-API-token-).

#### Option B: OAuth2.0 (recommended for Airbyte Cloud)

Airbyte Cloud handles the OAuth2.0 flow automatically. Select **OAuth2.0** as the authentication method and follow the prompts to authorize the connector with your Zendesk account.

For Airbyte Open Source, you can configure OAuth manually by registering an OAuth client in Zendesk. See [Using OAuth authentication with your application](https://support.zendesk.com/hc/en-us/articles/4408845965210-Using-OAuth-authentication-with-your-application) for details.

<!-- env:cloud -->

### Step 2: Set up the Zendesk Talk connector in Airbyte

**For Airbyte Cloud:**

1. [Log into your Airbyte Cloud](https://cloud.airbyte.com/workspaces) account.
2. In the left navigation bar, click **Sources**. In the top-right corner, click **+ New source**.
3. Find and select **Zendesk Talk** from the source type dropdown.
4. Enter the following fields:
   - **Subdomain**: Your Zendesk subdomain (for example, if your URL is `https://mycompany.zendesk.com`, enter `mycompany`).
   - **Authentication**: Select your authentication method and provide the required credentials.
   - **Start Date**: The date from which to start replicating data, in `YYYY-MM-DDT00:00:00Z` format (for example, `2020-10-15T00:00:00Z`). Data generated on or after this date is replicated.
5. Click **Set up source**.

<!-- /env:cloud -->

<!-- env:oss -->

**For Airbyte Open Source:**

1. Navigate to the Airbyte Open Source dashboard.
2. In the left navigation bar, click **Sources**. In the top-right corner, click **+ New source**.
3. Find and select **Zendesk Talk** from the source type dropdown.
4. Enter the following fields:
   - **Subdomain**: Your Zendesk subdomain (for example, if your URL is `https://mycompany.zendesk.com`, enter `mycompany`).
   - **Authentication**: Select **API Token**, then provide your Zendesk email address and API token.
   - **Start Date**: The date from which to start replicating data, in `YYYY-MM-DDT00:00:00Z` format (for example, `2020-10-15T00:00:00Z`). Data generated on or after this date is replicated.
5. Click **Set up source**.

<!-- /env:oss -->

## Supported sync modes

The **Zendesk Talk** source connector supports the following [sync modes](https://docs.airbyte.com/cloud/core-concepts#connection-sync-modes):

- Full Refresh
- Incremental Sync

## Supported streams

This connector syncs the following streams:

- [Account Overview](https://developer.zendesk.com/api-reference/voice/talk-api/stats/#show-account-overview)
- [Addresses](https://developer.zendesk.com/api-reference/voice/talk-api/addresses/#list-addresses)
- [Agents Activity](https://developer.zendesk.com/api-reference/voice/talk-api/stats/#list-agents-activity)
- [Agents Overview](https://developer.zendesk.com/api-reference/voice/talk-api/stats/#show-agents-overview)
- [Calls](https://developer.zendesk.com/api-reference/voice/talk-api/incremental_exports/#incremental-calls-export) (Incremental)
- [Call Legs](https://developer.zendesk.com/api-reference/voice/talk-api/incremental_exports/#incremental-call-legs-export) (Incremental)
- [Current Queue Activity](https://developer.zendesk.com/api-reference/voice/talk-api/stats/#show-current-queue-activity)
- [Greeting Categories](https://developer.zendesk.com/api-reference/voice/talk-api/greetings/#list-greeting-categories)
- [Greetings](https://developer.zendesk.com/api-reference/voice/talk-api/greetings/#list-greetings)
- [IVRs](https://developer.zendesk.com/api-reference/voice/talk-api/ivrs/#list-ivrs)
- [IVR Menus](https://developer.zendesk.com/api-reference/voice/talk-api/ivr_menus/#list-ivr-menus)
- [IVR Routes](https://developer.zendesk.com/api-reference/voice/talk-api/ivr_routes/#list-ivr-routes)
- [Phone Numbers](https://developer.zendesk.com/api-reference/voice/talk-api/phone_numbers/#list-phone-numbers)

:::note
The IVR, IVR Menus, and IVR Routes streams require the Zendesk Talk Professional or Enterprise plan.
:::

## Performance considerations

The connector is subject to [Zendesk Talk API rate limits](https://developer.zendesk.com/api-reference/voice/talk-api/introduction/#rate-limits):

| Endpoint | Rate limit |
|:--|:--|
| Most endpoints | 15,000 requests per 5 minutes |
| Current Queue Activity | 2,500 requests per 5 minutes |
| Incremental Exports (Calls, Call Legs) | 10 requests per minute |

The standard [Zendesk Support API rate limits](https://developer.zendesk.com/api-reference/introduction/rate-limits/) also apply. The connector automatically retries rate-limited requests using the `Retry-After` header. Under normal usage, you should not encounter rate limit issues. If you do, [create an issue](https://github.com/airbytehq/airbyte/issues).

## Data type map

| Integration Type | Airbyte Type |
|:-----------------|:-------------|
| `string`         | `string`     |
| `number`         | `number`     |
| `array`          | `array`      |
| `object`         | `object`     |

## Upgrading

For information about breaking changes and migration steps, see the [Zendesk Talk migration guide](./zendesk-talk-migrations.md).

## Changelog

<details>
  <summary>Expand to review</summary>

| Version | Date       | Pull Request                                             | Subject                                                                     |
|:--------|:-----------|:---------------------------------------------------------|:----------------------------------------------------------------------------|
| 2.0.8 | 2026-03-17 | [74395](https://github.com/airbytehq/airbyte/pull/74395) | Migrate to scopes object array format |
| 2.0.7 | 2026-03-10 | [74446](https://github.com/airbytehq/airbyte/pull/74446) | Update dependencies |
| 2.0.6 | 2026-02-24 | [73990](https://github.com/airbytehq/airbyte/pull/73990) | Update dependencies |
| 2.0.5 | 2026-02-17 | [73506](https://github.com/airbytehq/airbyte/pull/73506) | Update dependencies |
| 2.0.4 | 2026-02-10 | [72070](https://github.com/airbytehq/airbyte/pull/72070) | Update dependencies |
| 2.0.3 | 2026-02-03 | [72782](https://github.com/airbytehq/airbyte/pull/72782) | Upgrade CDK version to 7.8.1 |
| 2.0.2 | 2026-01-28 | [72424](https://github.com/airbytehq/airbyte/pull/72424) | Update breaking change deadline from Jan 31 to Jan 30 |
| 2.0.1 | 2026-01-27 | [72383](https://github.com/airbytehq/airbyte/pull/72383) | Fix OAuth race condition with concurrent token refresh |
| 2.0.0 | 2026-01-21 | [71857](https://github.com/airbytehq/airbyte/pull/71857) | Add OAuth2.0 with refresh token support. Users who authenticate via OAuth must re-authenticate. |
| 1.2.29 | 2026-01-14 | [71686](https://github.com/airbytehq/airbyte/pull/71686) | Update dependencies |
| 1.2.28 | 2025-12-18 | [70683](https://github.com/airbytehq/airbyte/pull/70683) | Update dependencies |
| 1.2.27 | 2025-11-25 | [70102](https://github.com/airbytehq/airbyte/pull/70102) | Update dependencies |
| 1.2.26 | 2025-11-18 | [69569](https://github.com/airbytehq/airbyte/pull/69569) | Update dependencies |
| 1.2.25 | 2025-10-29 | [68944](https://github.com/airbytehq/airbyte/pull/68944) | Update dependencies |
| 1.2.24 | 2025-10-22 | [68591](https://github.com/airbytehq/airbyte/pull/68591) | Add `suggestedStreams` |
| 1.2.23 | 2025-10-21 | [68411](https://github.com/airbytehq/airbyte/pull/68411) | Update dependencies |
| 1.2.22 | 2025-10-14 | [67991](https://github.com/airbytehq/airbyte/pull/67991) | Update dependencies |
| 1.2.21 | 2025-10-07 | [67246](https://github.com/airbytehq/airbyte/pull/67246) | Update dependencies |
| 1.2.20 | 2025-09-30 | [66855](https://github.com/airbytehq/airbyte/pull/66855) | Update dependencies |
| 1.2.19 | 2025-09-24 | [66473](https://github.com/airbytehq/airbyte/pull/66473) | Update dependencies |
| 1.2.18 | 2025-09-09 | [65721](https://github.com/airbytehq/airbyte/pull/65721) | Update dependencies |
| 1.2.17 | 2025-08-24 | [65426](https://github.com/airbytehq/airbyte/pull/65426) | Update dependencies |
| 1.2.16 | 2025-08-10 | [64871](https://github.com/airbytehq/airbyte/pull/64871) | Update dependencies |
| 1.2.15 | 2025-08-02 | [64320](https://github.com/airbytehq/airbyte/pull/64320) | Update dependencies |
| 1.2.14 | 2025-07-27 | [64081](https://github.com/airbytehq/airbyte/pull/64081) | Update dependencies |
| 1.2.13 | 2025-07-19 | [63611](https://github.com/airbytehq/airbyte/pull/63611) | Update dependencies |
| 1.2.12 | 2025-07-12 | [63180](https://github.com/airbytehq/airbyte/pull/63180) | Update dependencies |
| 1.2.11 | 2025-07-05 | [62730](https://github.com/airbytehq/airbyte/pull/62730) | Update dependencies |
| 1.2.10 | 2025-06-28 | [62224](https://github.com/airbytehq/airbyte/pull/62224) | Update dependencies |
| 1.2.9 | 2025-06-21 | [61753](https://github.com/airbytehq/airbyte/pull/61753) | Update dependencies |
| 1.2.8 | 2025-06-15 | [61223](https://github.com/airbytehq/airbyte/pull/61223) | Update dependencies |
| 1.2.7 | 2025-05-24 | [60770](https://github.com/airbytehq/airbyte/pull/60770) | Update dependencies |
| 1.2.6 | 2025-05-10 | [59917](https://github.com/airbytehq/airbyte/pull/59917) | Update dependencies |
| 1.2.5 | 2025-05-04 | [58933](https://github.com/airbytehq/airbyte/pull/58933) | Update dependencies |
| 1.2.4 | 2025-04-19 | [58541](https://github.com/airbytehq/airbyte/pull/58541) | Update dependencies |
| 1.2.3 | 2025-04-13 | [58053](https://github.com/airbytehq/airbyte/pull/58053) | Update dependencies |
| 1.2.2 | 2025-04-05 | [56838](https://github.com/airbytehq/airbyte/pull/56838) | Update dependencies |
| 1.2.1 | 2025-03-22 | [48245](https://github.com/airbytehq/airbyte/pull/48245) | Update dependencies |
| 1.2.0 | 2025-02-07 | [50956](https://github.com/airbytehq/airbyte/pull/50956) | Restore Unit Test |
| 1.1.0-rc.1  | 2024-10-31 | [47313](https://github.com/airbytehq/airbyte/pull/47313) | Migrate to Manifest-only |
| 1.0.21 | 2024-10-29 | [47082](https://github.com/airbytehq/airbyte/pull/47082) | Update dependencies |
| 1.0.20 | 2024-10-12 | [46861](https://github.com/airbytehq/airbyte/pull/46861) | Update dependencies |
| 1.0.19 | 2024-10-05 | [46394](https://github.com/airbytehq/airbyte/pull/46394) | Update dependencies |
| 1.0.18 | 2024-09-28 | [46149](https://github.com/airbytehq/airbyte/pull/46149) | Update dependencies |
| 1.0.17 | 2024-09-21 | [45783](https://github.com/airbytehq/airbyte/pull/45783) | Update dependencies |
| 1.0.16 | 2024-09-14 | [45524](https://github.com/airbytehq/airbyte/pull/45524) | Update dependencies |
| 1.0.15 | 2024-09-07 | [45301](https://github.com/airbytehq/airbyte/pull/45301) | Update dependencies |
| 1.0.14 | 2024-08-31 | [45019](https://github.com/airbytehq/airbyte/pull/45019) | Update dependencies |
| 1.0.13 | 2024-08-24 | [44624](https://github.com/airbytehq/airbyte/pull/44624) | Update dependencies |
| 1.0.12 | 2024-08-17 | [44214](https://github.com/airbytehq/airbyte/pull/44214) | Update dependencies |
| 1.0.11 | 2024-08-10 | [43558](https://github.com/airbytehq/airbyte/pull/43558) | Update dependencies |
| 1.0.10 | 2024-08-03 | [43203](https://github.com/airbytehq/airbyte/pull/43203) | Update dependencies |
| 1.0.9 | 2024-07-27 | [42669](https://github.com/airbytehq/airbyte/pull/42669) | Update dependencies |
| 1.0.8 | 2024-07-20 | [42328](https://github.com/airbytehq/airbyte/pull/42328) | Update dependencies |
| 1.0.7 | 2024-07-13 | [41727](https://github.com/airbytehq/airbyte/pull/41727) | Update dependencies |
| 1.0.6 | 2024-07-10 | [41350](https://github.com/airbytehq/airbyte/pull/41350) | Update dependencies |
| 1.0.5 | 2024-07-09 | [41119](https://github.com/airbytehq/airbyte/pull/41119) | Update dependencies |
| 1.0.4 | 2024-07-06 | [40855](https://github.com/airbytehq/airbyte/pull/40855) | Update dependencies |
| 1.0.3 | 2024-06-25 | [40278](https://github.com/airbytehq/airbyte/pull/40278) | Update dependencies |
| 1.0.2 | 2024-06-22 | [40056](https://github.com/airbytehq/airbyte/pull/40056) | Update dependencies |
| 1.0.1 | 2024-06-04 | [39036](https://github.com/airbytehq/airbyte/pull/39036) | [autopull] Upgrade base image to v1.2.1 |
| 1.0.0 | 2024-05-06 | [35780](https://github.com/airbytehq/airbyte/pull/35780) | Migrate implementation to low-code CDK |
| 0.2.1 | 2024-05-02 | [36625](https://github.com/airbytehq/airbyte/pull/36625) | Schema descriptions and CDK 0.80.0 |
| 0.2.0 | 2024-03-25 | [36459](https://github.com/airbytehq/airbyte/pull/36459) | Unpin CDK version, add record counts in state messages |
| 0.1.13 | 2024-03-04 | [35783](https://github.com/airbytehq/airbyte/pull/35783) | Change order of authentication methods in spec |
| 0.1.12 | 2024-02-12 | [35156](https://github.com/airbytehq/airbyte/pull/35156) | Manage dependencies with Poetry. |
| 0.1.11 | 2024-01-12 | [34204](https://github.com/airbytehq/airbyte/pull/34204) | Prepare for airbyte-lib |
| 0.1.10 | 2023-12-04 | [33030](https://github.com/airbytehq/airbyte/pull/33030) | Base image migration: remove Dockerfile and use python-connector-base image |
| 0.1.9 | 2023-08-03 | [29031](https://github.com/airbytehq/airbyte/pull/29031) | Reverted `advancedAuth` spec changes |
| 0.1.8 | 2023-08-01 | [28910](https://github.com/airbytehq/airbyte/pull/28910) | Updated `advancedAuth` broken references |
| 0.1.7 | 2023-02-10 | [22815](https://github.com/airbytehq/airbyte/pull/22815) | Specified date formatting in specification |
| 0.1.6 | 2023-01-27 | [22028](https://github.com/airbytehq/airbyte/pull/22028) | Set `AvailabilityStrategy` for streams explicitly to `None` |
| 0.1.5 | 2022-09-29 | [17362](https://github.com/airbytehq/airbyte/pull/17362) | always use the latest CDK version |
| 0.1.4 | 2022-08-19 | [15764](https://github.com/airbytehq/airbyte/pull/15764) | Support OAuth2.0 |
| 0.1.3 | 2021-11-11 | [7173](https://github.com/airbytehq/airbyte/pull/7173) | Fix pagination and migrate to CDK |

</details>

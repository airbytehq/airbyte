# PartnerStack

<HideInUI>

This page contains the setup guide and reference information for the [PartnerStack](https://partnerstack.com/) source connector.

</HideInUI>

## Prerequisites

- A PartnerStack account with access to the Vendor dashboard
- PartnerStack API keys (public key and private key)

## Setup guide

### Step 1: Obtain your PartnerStack API keys

1. Log in to your [PartnerStack Vendor dashboard](https://app.partnerstack.com/).
2. Navigate to **Settings > Integrations > PartnerStack API Keys**.
3. Copy your **Public key** and **Private key**. The connector uses [Basic authentication](https://docs.partnerstack.com/reference/auth), where the public key is the username and the private key is the password.

:::note
PartnerStack provides separate test and production API keys. Test keys create test customers and do not generate rewards. Use production keys for syncing real data.
:::

### Step 2: Set up the PartnerStack connector in Airbyte

1. Enter a name for the PartnerStack connector.
2. Enter your **Public key**.
3. Enter your **Private key**.
4. Optionally, enter a **Start date** in `YYYY-MM-DDTHH:MM:SSZ` format (for example, `2017-01-25T00:00:00Z`). Only data created or updated after this date is replicated. If you don't set a start date, all available data is replicated.
5. Click **Set up source** and wait for the tests to complete.

<HideInUI>

## Supported sync modes

The PartnerStack source connector supports the following [sync modes](https://docs.airbyte.com/cloud/core-concepts/#connection-sync-modes):

- Full Refresh
- Incremental - Append

## Supported streams

The PartnerStack source connector supports the following streams. All streams read from the [PartnerStack Vendor API v2](https://docs.partnerstack.com/reference).

| Stream | Sync mode | Cursor field |
| :--- | :--- | :--- |
| [Customers](https://docs.partnerstack.com/reference/get_v2-customers-2) | Incremental | `updated_at` |
| [Deals](https://docs.partnerstack.com/reference/get_v2-deals) | Incremental | `updated_at` |
| [Groups](https://docs.partnerstack.com/reference/get_v2-groups) | Incremental | `updated_at` |
| [Leads](https://docs.partnerstack.com/reference/get_v2-leads) | Incremental | `updated_at` |
| [Partnerships](https://docs.partnerstack.com/reference/get_v2-partnerships-2) | Incremental | `updated_at` |
| [Rewards](https://docs.partnerstack.com/reference/get_v2-rewards-2) | Full Refresh | - |
| [Transactions](https://docs.partnerstack.com/reference/get_v2-transactions-2) | Full Refresh | - |

## Performance considerations

The PartnerStack API enforces a rate limit of 4,000 requests per minute per IP address. The connector should not run into this limit under normal usage. If you receive HTTP 429 responses, reduce the sync frequency.

## Limitations

- The connector uses the PartnerStack **Vendor API**, which authenticates with Basic Auth (public key and private key). It does not use the Partner API, which requires Bearer token authentication.
- The Rewards and Transactions streams do not support incremental sync by `updated_at`. They filter by `min_created` using the configured start date, so they perform a full refresh of all records created after the start date on each sync.

</HideInUI>

## Changelog

<details>
  <summary>Expand to review</summary>

| Version | Date       | Pull Request                                             | Subject                                     |
|:--------|:-----------|:---------------------------------------------------------|:--------------------------------------------|
| 0.3.12 | 2026-03-10 | [74086](https://github.com/airbytehq/airbyte/pull/74086) | Add missing fields (test, metadata) to Transactions stream schema |
| 0.3.11 | 2025-05-24 | [60453](https://github.com/airbytehq/airbyte/pull/60453) | Update dependencies |
| 0.3.10 | 2025-05-10 | [60087](https://github.com/airbytehq/airbyte/pull/60087) | Update dependencies |
| 0.3.9 | 2025-05-03 | [59453](https://github.com/airbytehq/airbyte/pull/59453) | Update dependencies |
| 0.3.8 | 2025-04-27 | [59089](https://github.com/airbytehq/airbyte/pull/59089) | Update dependencies |
| 0.3.7 | 2025-04-19 | [58489](https://github.com/airbytehq/airbyte/pull/58489) | Update dependencies |
| 0.3.6 | 2025-04-12 | [57922](https://github.com/airbytehq/airbyte/pull/57922) | Update dependencies |
| 0.3.5 | 2025-04-05 | [57330](https://github.com/airbytehq/airbyte/pull/57330) | Update dependencies |
| 0.3.4 | 2025-03-29 | [56787](https://github.com/airbytehq/airbyte/pull/56787) | Update dependencies |
| 0.3.3 | 2025-03-22 | [56171](https://github.com/airbytehq/airbyte/pull/56171) | Update dependencies |
| 0.3.2 | 2025-03-08 | [55537](https://github.com/airbytehq/airbyte/pull/55537) | Update dependencies |
| 0.3.1 | 2025-03-01 | [53962](https://github.com/airbytehq/airbyte/pull/53962) | Update dependencies |
| 0.3.0 | 2025-02-26 | [47280](https://github.com/airbytehq/airbyte/pull/47280) | Migrate to Manifest-only |
| 0.2.8 | 2025-02-01 | [52541](https://github.com/airbytehq/airbyte/pull/52541) | Update dependencies |
| 0.2.7 | 2025-01-18 | [51913](https://github.com/airbytehq/airbyte/pull/51913) | Update dependencies |
| 0.2.6 | 2025-01-11 | [51344](https://github.com/airbytehq/airbyte/pull/51344) | Update dependencies |
| 0.2.5 | 2025-01-04 | [50934](https://github.com/airbytehq/airbyte/pull/50934) | Update dependencies |
| 0.2.4 | 2024-12-28 | [50723](https://github.com/airbytehq/airbyte/pull/50723) | Update dependencies |
| 0.2.3 | 2024-12-21 | [50246](https://github.com/airbytehq/airbyte/pull/50246) | Update dependencies |
| 0.2.2 | 2024-12-14 | [49675](https://github.com/airbytehq/airbyte/pull/49675) | Update dependencies |
| 0.2.1 | 2024-12-11 | [49085](https://github.com/airbytehq/airbyte/pull/49085) | Starting with this version, the Docker image is now rootless. Please note that this and future versions will not be compatible with Airbyte versions earlier than 0.64 |
| 0.2.0 | 2024-12-03 | [48782](https://github.com/airbytehq/airbyte/pull/48782) | Add Incremental feature |
| 0.1.25 | 2024-11-04 | [48184](https://github.com/airbytehq/airbyte/pull/48184) | Update dependencies |
| 0.1.24 | 2024-10-29 | [47762](https://github.com/airbytehq/airbyte/pull/47762) | Update dependencies |
| 0.1.23 | 2024-10-28 | [47045](https://github.com/airbytehq/airbyte/pull/47045) | Update dependencies |
| 0.1.22 | 2024-10-12 | [46808](https://github.com/airbytehq/airbyte/pull/46808) | Update dependencies |
| 0.1.21 | 2024-10-05 | [46452](https://github.com/airbytehq/airbyte/pull/46452) | Update dependencies |
| 0.1.20 | 2024-09-28 | [46111](https://github.com/airbytehq/airbyte/pull/46111) | Update dependencies |
| 0.1.19 | 2024-09-21 | [45775](https://github.com/airbytehq/airbyte/pull/45775) | Update dependencies |
| 0.1.18 | 2024-09-14 | [45506](https://github.com/airbytehq/airbyte/pull/45506) | Update dependencies |
| 0.1.17 | 2024-09-07 | [45294](https://github.com/airbytehq/airbyte/pull/45294) | Update dependencies |
| 0.1.16 | 2024-08-31 | [45053](https://github.com/airbytehq/airbyte/pull/45053) | Update dependencies |
| 0.1.15 | 2024-08-24 | [44712](https://github.com/airbytehq/airbyte/pull/44712) | Update dependencies |
| 0.1.14 | 2024-08-17 | [44358](https://github.com/airbytehq/airbyte/pull/44358) | Update dependencies |
| 0.1.13 | 2024-08-12 | [43738](https://github.com/airbytehq/airbyte/pull/43738) | Update dependencies |
| 0.1.12 | 2024-08-10 | [43692](https://github.com/airbytehq/airbyte/pull/43692) | Update dependencies |
| 0.1.11 | 2024-08-03 | [42757](https://github.com/airbytehq/airbyte/pull/42757) | Update dependencies |
| 0.1.10 | 2024-07-20 | [42338](https://github.com/airbytehq/airbyte/pull/42338) | Update dependencies |
| 0.1.9 | 2024-07-13 | [41757](https://github.com/airbytehq/airbyte/pull/41757) | Update dependencies |
| 0.1.8 | 2024-07-10 | [41466](https://github.com/airbytehq/airbyte/pull/41466) | Update dependencies |
| 0.1.7 | 2024-07-09 | [41306](https://github.com/airbytehq/airbyte/pull/41306) | Update dependencies |
| 0.1.6 | 2024-07-06 | [40881](https://github.com/airbytehq/airbyte/pull/40881) | Update dependencies |
| 0.1.5 | 2024-06-25 | [40378](https://github.com/airbytehq/airbyte/pull/40378) | Update dependencies |
| 0.1.4 | 2024-06-22 | [40024](https://github.com/airbytehq/airbyte/pull/40024) | Update dependencies |
| 0.1.3 | 2024-06-13 | [37595](https://github.com/airbytehq/airbyte/pull/37595) | Change `last_records` to `last_record` |
| 0.1.2 | 2024-06-04 | [38964](https://github.com/airbytehq/airbyte/pull/38964) | [autopull] Upgrade base image to v1.2.1 |
| 0.1.1 | 2024-05-21 | [38484](https://github.com/airbytehq/airbyte/pull/38484) | [autopull] base image + poetry + up_to_date |
| 0.1.0 | 2022-10-27 | | Add PartnerStack source connector |

</details>

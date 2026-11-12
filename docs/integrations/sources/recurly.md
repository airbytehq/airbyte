# Recurly

This page contains the setup guide and reference information for the Recurly source connector. The connector reads data from the [Recurly v3 API](https://recurly.com/developers/api/v2021-02-25/index.html) (version `v2021-02-25`).

## Prerequisites

- A Recurly site
- A Recurly user with a role that includes the Integration permission, so you can view API credentials
- A private API key for the site you want to sync

## Setup guide

### Step 1: Get a Recurly API key

1. Sign in to Recurly as a user with the Integration permission.
2. Go to **Integrations** > **API Credentials**.
3. Copy an existing private API key, or add a new private key for Airbyte.

Recurly private API keys grant full access to your site's data, and Recurly doesn't offer read-only keys. Creating a dedicated key for Airbyte lets you revoke its access without affecting other integrations. For more information, see [Recurly API keys](https://docs.recurly.com/docs/api-keys).

### Step 2: Set up the Recurly connector in Airbyte

1. In Airbyte, go to **Sources** and add a new source. Select **Recurly**.
2. For **API Key**, paste the private API key from Step 1.
3. (Optional) For **Start Date**, enter the UTC date and time to start replicating data from, in the format `YYYY-MM-DDTHH:mm:ssZ`. If you leave it empty, the connector replicates the last five years of data.
4. (Optional) For **End Date**, enter the UTC date and time to stop replicating data at, in the format `YYYY-MM-DDTHH:mm:ssZ`. Records updated after this time aren't replicated. If you leave it empty, the connector replicates data up to the time of the sync.
5. (Optional) For **Number of concurrent threads**, enter the number of requests the connector sends to Recurly in parallel, from 1 to 20. The default is 10.
6. (Optional) For **Days in length for each API call to get data**, enter the number of days of data the connector requests at a time from the accounts stream, from 1 to 365. The default is 30. Smaller values result in more API calls but better concurrency.
7. (Optional) Turn on **Use Sandbox Environment** if the API key belongs to a Recurly sandbox site. Sandbox sites have a lower rate limit than production sites.
8. Click **Set up source**.

## Supported sync modes

The Recurly source connector supports the following sync modes:

- Full Refresh
- Incremental

The Export Dates, Gift Cards, External Subscriptions, External Subscription Payment Phases, and Usage Records streams support Full Refresh only. All other streams support incremental syncs. Most incremental streams use `updated_at` as the cursor. The Account Notes stream uses `created_at`.

## Supported streams

- [Accounts](https://docs.recurly.com/docs/accounts)
- [Account Acquisitions](https://recurly.com/developers/api/v2021-02-25/index.html#tag/account_acquisition)
- [Account Coupon Redemptions](https://docs.recurly.com/docs/coupons#redemptions)
- [Account Notes](https://docs.recurly.com/docs/accounts#account-notes)
- [Add Ons](https://docs.recurly.com/docs/plans#add-ons-1)
- [Billing Infos](https://docs.recurly.com/docs/accounts#billing-info)
- [Coupons](https://docs.recurly.com/docs/coupons)
- [Credit Payments](https://docs.recurly.com/docs/invoices)
- [Export Dates](https://docs.recurly.com/docs/export-overview) (Full Refresh only)
- [External Subscriptions](https://developers.recurly.com/api/v2021-02-25/index.html#operation/list_external_subscriptions)
- [External Subscription Payment Phases](https://developers.recurly.com/api/v2021-02-25/index.html#operation/list_external_subscription_external_payment_phases)
- [Gift Cards](https://docs.recurly.com/docs/gift-cards)
- [Invoices](https://docs.recurly.com/docs/invoices)
- [Items](https://developers.recurly.com/api/v2021-02-25/index.html#operation/list_items)
- [Line Items](https://docs.recurly.com/docs/invoices#line-items)
- [Measured Units](https://recurly.com/developers/api/v2021-02-25/index.html#tag/measured_unit)
- [Plans](https://docs.recurly.com/docs/plans)
- [Shipping Addresses](https://docs.recurly.com/docs/shipping-addresses)
- [Shipping Methods](https://docs.recurly.com/docs/shipping#shipping-methods)
- [Subscriptions](https://docs.recurly.com/docs/subscriptions)
- [Transactions](https://docs.recurly.com/docs/transactions)
- [Unique Coupons](https://docs.recurly.com/docs/bulk-unique-coupons)
- Unique Coupons Parent
- [Usage Records](https://docs.recurly.com/docs/usage-based-billing)

The Usage Records stream includes both billed and unbilled usage.

Some streams only return data when the matching feature is enabled on your Recurly site:

| Stream | Required Recurly feature |
| :----- | :----------------------- |
| Gift Cards | Gift cards |
| External Subscriptions, External Subscription Payment Phases | External subscriptions |
| Usage Records | Usage-based billing |
| Items | Item catalog, which also requires Credit Invoices |

If Recurly reports that your site lacks the required feature for one of these streams or for Account Acquisitions, the connector logs a message, skips the stream, and the sync continues.

The Account Coupon Redemptions, Account Notes, Billing Infos, and Shipping Addresses streams make one request per account, so they can take longer to sync on sites with many accounts.

## Limitations and troubleshooting

### Rate limits

Recurly limits API requests over a sliding five-minute window. By default, production sites allow 5,000 GET requests and sandbox sites allow 2,000 requests in that window. The connector paces its requests to stay within the limit for the site type you select with **Use Sandbox Environment**. See [Recurly API limits](https://recurly.com/developers/api/v2021-02-25/index.html#section/Getting-Started/Limits).

Recurly applies the limit to the whole site, but the connector only tracks its own requests. If other connections or integrations use the same Recurly site, the connector can still receive HTTP 429 responses. The connector retries rate-limited and server error responses up to five times with exponential backoff.

The Usage Records stream reads every subscription on every sync, then makes one API request per subscription add-on. On large sites, it can be slow and use a large share of the rate limit. Enable this stream only when you need usage records. If your connection automatically propagates new streams after a schema refresh, check that Usage Records wasn't selected unintentionally.

### Authentication errors

If Recurly returns HTTP 401 or 403, the sync fails with a configuration error. Make sure the API key is an active private key for the site you want to sync, then update the **API Key** field.

## IP allow list

If you use Airbyte Cloud and your organization restricts access to specific IPs, add the [Airbyte Cloud IP addresses](https://docs.airbyte.com/platform/operating-airbyte/ip-allowlist) to your allow list.

## Changelog

<details>
  <summary>Expand to review</summary>

| Version | Date       | Pull Request                                             | Subject                                                                              |
| :------ | :--------- | :------------------------------------------------------- | :----------------------------------------------------------------------------------- |
| 1.4.0 | 2026-11-12 | [91305](https://github.com/airbytehq/airbyte/pull/91305) | Add account_acquisitions, gift_cards, external_subscriptions, external_subscription_payment_phases, usage_records and items streams |
| 1.3.71 | 2026-11-10 | [91303](https://github.com/airbytehq/airbyte/pull/91303) | Pace requests to Recurly's published rate limits, retry rate-limited and server error responses with exponential backoff, show actionable API key errors, and accept start and end dates saved without the trailing `Z` |
| 1.3.70 | 2026-11-10 | [91708](https://github.com/airbytehq/airbyte/pull/91708) | Update dependencies |
| 1.3.69 | 2026-11-03 | [90721](https://github.com/airbytehq/airbyte/pull/90721) | Update dependencies |
| 1.3.68 | 2026-10-20 | [89408](https://github.com/airbytehq/airbyte/pull/89408) | Update dependencies |
| 1.3.67 | 2026-10-13 | [88767](https://github.com/airbytehq/airbyte/pull/88767) | Update dependencies |
| 1.3.66 | 2026-10-06 | [88013](https://github.com/airbytehq/airbyte/pull/88013) | Update dependencies |
| 1.3.65 | 2026-09-29 | [87315](https://github.com/airbytehq/airbyte/pull/87315) | Update dependencies |
| 1.3.64 | 2026-09-22 | [86794](https://github.com/airbytehq/airbyte/pull/86794) | Update dependencies |
| 1.3.63 | 2026-09-15 | [86212](https://github.com/airbytehq/airbyte/pull/86212) | Update dependencies |
| 1.3.62 | 2026-09-08 | [85632](https://github.com/airbytehq/airbyte/pull/85632) | Update dependencies |
| 1.3.61 | 2026-08-18 | [84729](https://github.com/airbytehq/airbyte/pull/84729) | Update dependencies |
| 1.3.60 | 2026-08-11 | [84098](https://github.com/airbytehq/airbyte/pull/84098) | Update dependencies |
| 1.3.59 | 2026-07-28 | [83194](https://github.com/airbytehq/airbyte/pull/83194) | Update to CDK 7.23.8 (fixes AirbyteCustomCodeNotPermittedError for bundled custom components) and remove the temporary Cloud version override |
| 1.3.58 | 2026-07-28 | [1082](https://github.com/airbytehq/airbyte-python-cdk/issues/1082) | Roll Cloud back to 1.3.56 — 1.3.57 is built on SDM 7.23.7, which breaks bundled custom components |
| 1.3.57 | 2026-07-28 | [83069](https://github.com/airbytehq/airbyte/pull/83069) | Update dependencies |
| 1.3.56 | 2026-07-21 | [82560](https://github.com/airbytehq/airbyte/pull/82560) | Update dependencies |
| 1.3.55 | 2026-07-14 | [81973](https://github.com/airbytehq/airbyte/pull/81973) | Update dependencies |
| 1.3.54 | 2026-06-30 | [81209](https://github.com/airbytehq/airbyte/pull/81209) | Update dependencies |
| 1.3.53 | 2026-06-23 | [80563](https://github.com/airbytehq/airbyte/pull/80563) | Update dependencies |
| 1.3.52 | 2026-06-16 | [80005](https://github.com/airbytehq/airbyte/pull/80005) | Update dependencies |
| 1.3.51 | 2026-06-09 | [79468](https://github.com/airbytehq/airbyte/pull/79468) | Update dependencies |
| 1.3.50 | 2026-06-02 | [78924](https://github.com/airbytehq/airbyte/pull/78924) | Update dependencies |
| 1.3.49 | 2026-04-28 | [77376](https://github.com/airbytehq/airbyte/pull/77376) | Update dependencies |
| 1.3.48 | 2026-04-21 | [76720](https://github.com/airbytehq/airbyte/pull/76720) | Update dependencies |
| 1.3.47 | 2026-04-13 | [76276](https://github.com/airbytehq/airbyte/pull/76276) | Rename "concurrent workers" to "concurrent threads" in connector spec |
| 1.3.46 | 2026-03-24 | [75379](https://github.com/airbytehq/airbyte/pull/75379) | Update dependencies |
| 1.3.45 | 2026-03-10 | [74639](https://github.com/airbytehq/airbyte/pull/74639) | Update dependencies |
| 1.3.44 | 2026-03-03 | [73886](https://github.com/airbytehq/airbyte/pull/73886) | Update dependencies |
| 1.3.43 | 2026-02-17 | [73522](https://github.com/airbytehq/airbyte/pull/73522) | Update dependencies |
| 1.3.42 | 2026-02-03 | [72656](https://github.com/airbytehq/airbyte/pull/72656) | Update dependencies |
| 1.3.41 | 2026-01-20 | [72016](https://github.com/airbytehq/airbyte/pull/72016) | Update dependencies |
| 1.3.40 | 2026-01-14 | [71471](https://github.com/airbytehq/airbyte/pull/71471) | Update dependencies |
| 1.3.39 | 2025-12-18 | [70642](https://github.com/airbytehq/airbyte/pull/70642) | Update dependencies |
| 1.3.38 | 2025-11-25 | [70003](https://github.com/airbytehq/airbyte/pull/70003) | Update dependencies |
| 1.3.37 | 2025-11-18 | [69622](https://github.com/airbytehq/airbyte/pull/69622) | Update dependencies |
| 1.3.36 | 2025-10-29 | [68903](https://github.com/airbytehq/airbyte/pull/68903) | Update dependencies |
| 1.3.35 | 2025-10-21 | [68341](https://github.com/airbytehq/airbyte/pull/68341) | Update dependencies |
| 1.3.34 | 2025-10-14 | [67882](https://github.com/airbytehq/airbyte/pull/67882) | Update dependencies |
| 1.3.33 | 2025-10-08 | [67545](https://github.com/airbytehq/airbyte/pull/67545) | Update dependencies |
| 1.3.32 | 2025-09-30 | [66434](https://github.com/airbytehq/airbyte/pull/66434) | Update dependencies |
| 1.3.31 | 2025-09-09 | [65702](https://github.com/airbytehq/airbyte/pull/65702) | Update dependencies |
| 1.3.30 | 2025-08-24 | [65439](https://github.com/airbytehq/airbyte/pull/65439) | Update dependencies |
| 1.3.29 | 2025-08-16 | [64996](https://github.com/airbytehq/airbyte/pull/64996) | Update dependencies |
| 1.3.28 | 2025-08-03 | [64476](https://github.com/airbytehq/airbyte/pull/64476) | Update dependencies |
| 1.3.27 | 2025-07-20 | [63657](https://github.com/airbytehq/airbyte/pull/63657) | Update dependencies |
| 1.3.26 | 2025-07-07 | [63356](https://github.com/airbytehq/airbyte/pull/63356) | Update Schema and add configurable concurrency |
| 1.3.25 | 2025-07-05 | [62679](https://github.com/airbytehq/airbyte/pull/62679) | Update dependencies |
| 1.3.24 | 2025-06-28 | [61292](https://github.com/airbytehq/airbyte/pull/61292) | Update dependencies |
| 1.3.23 | 2025-06-23 | [46722](https://github.com/airbytehq/airbyte/pull/46722) | Fixes timestamp pattern for UI to match what connector expects |
| 1.3.22 | 2025-05-24 | [60470](https://github.com/airbytehq/airbyte/pull/60470) | Update dependencies |
| 1.3.21 | 2025-05-10 | [60117](https://github.com/airbytehq/airbyte/pull/60117) | Update dependencies |
| 1.3.20 | 2025-05-03 | [59488](https://github.com/airbytehq/airbyte/pull/59488) | Update dependencies |
| 1.3.19 | 2025-04-27 | [59059](https://github.com/airbytehq/airbyte/pull/59059) | Update dependencies |
| 1.3.18 | 2025-04-19 | [58512](https://github.com/airbytehq/airbyte/pull/58512) | Update dependencies |
| 1.3.17 | 2025-04-12 | [57862](https://github.com/airbytehq/airbyte/pull/57862) | Update dependencies |
| 1.3.16 | 2025-04-05 | [57342](https://github.com/airbytehq/airbyte/pull/57342) | Update dependencies |
| 1.3.15 | 2025-03-29 | [56797](https://github.com/airbytehq/airbyte/pull/56797) | Update dependencies |
| 1.3.14 | 2025-03-22 | [56238](https://github.com/airbytehq/airbyte/pull/56238) | Update dependencies |
| 1.3.13 | 2025-03-08 | [55054](https://github.com/airbytehq/airbyte/pull/55054) | Update dependencies |
| 1.3.12 | 2025-02-23 | [54550](https://github.com/airbytehq/airbyte/pull/54550) | Update dependencies |
| 1.3.11 | 2025-02-15 | [54010](https://github.com/airbytehq/airbyte/pull/54010) | Update dependencies |
| 1.3.10 | 2025-02-08 | [53507](https://github.com/airbytehq/airbyte/pull/53507) | Update dependencies |
| 1.3.9 | 2025-02-01 | [52982](https://github.com/airbytehq/airbyte/pull/52982) | Update dependencies |
| 1.3.8 | 2025-01-25 | [52493](https://github.com/airbytehq/airbyte/pull/52493) | Update dependencies |
| 1.3.7 | 2025-01-18 | [51864](https://github.com/airbytehq/airbyte/pull/51864) | Update dependencies |
| 1.3.6 | 2025-01-11 | [51351](https://github.com/airbytehq/airbyte/pull/51351) | Update dependencies |
| 1.3.5 | 2024-12-28 | [50684](https://github.com/airbytehq/airbyte/pull/50684) | Update dependencies |
| 1.3.4 | 2024-12-21 | [50289](https://github.com/airbytehq/airbyte/pull/50289) | Update dependencies |
| 1.3.3 | 2024-12-14 | [49718](https://github.com/airbytehq/airbyte/pull/49718) | Update dependencies |
| 1.3.2 | 2024-12-12 | [49333](https://github.com/airbytehq/airbyte/pull/49333) | Update dependencies |
| 1.3.1 | 2024-12-11 | [49091](https://github.com/airbytehq/airbyte/pull/49091) | Starting with this version, the Docker image is now rootless. Please note that this and future versions will not be compatible with Airbyte versions earlier than 0.64 |
| 1.3.0 | 2024-11-13 | [48474](https://github.com/airbytehq/airbyte/pull/48474) | Remove definition and schema redundancy, update to latest CDK and make compatibility with builder |
| 1.2.0 | 2024-11-04 | [47290](https://github.com/airbytehq/airbyte/pull/47290) | Migrate to manifest only format |
| 1.1.13 | 2024-11-04 | [48248](https://github.com/airbytehq/airbyte/pull/48248) | Update dependencies |
| 1.1.12 | 2024-10-28 | [47067](https://github.com/airbytehq/airbyte/pull/47067) | Update dependencies |
| 1.1.11 | 2024-10-12 | [46829](https://github.com/airbytehq/airbyte/pull/46829) | Update dependencies |
| 1.1.10 | 2024-10-05 | [46456](https://github.com/airbytehq/airbyte/pull/46456) | Update dependencies |
| 1.1.9 | 2024-09-28 | [46140](https://github.com/airbytehq/airbyte/pull/46140) | Update dependencies |
| 1.1.8 | 2024-09-21 | [45764](https://github.com/airbytehq/airbyte/pull/45764) | Update dependencies |
| 1.1.7 | 2024-09-14 | [45471](https://github.com/airbytehq/airbyte/pull/45471) | Update dependencies |
| 1.1.6 | 2024-09-07 | [45274](https://github.com/airbytehq/airbyte/pull/45274) | Update dependencies |
| 1.1.5 | 2024-08-31 | [45050](https://github.com/airbytehq/airbyte/pull/45050) | Update dependencies |
| 1.1.4 | 2024-08-24 | [44742](https://github.com/airbytehq/airbyte/pull/44742) | Update dependencies |
| 1.1.3 | 2024-08-17 | [44210](https://github.com/airbytehq/airbyte/pull/44210) | Update dependencies |
| 1.1.2 | 2024-08-10 | [43472](https://github.com/airbytehq/airbyte/pull/43472) | Update dependencies |
| 1.1.1 | 2024-08-03 | [43144](https://github.com/airbytehq/airbyte/pull/43144) | Update dependencies |
| 1.1.0 | 2024-07-24 | [40729](https://github.com/airbytehq/airbyte/pull/40729) | Migrate connector to low code |
| 1.0.12 | 2024-07-20 | [42206](https://github.com/airbytehq/airbyte/pull/42206) | Update dependencies |
| 1.0.11 | 2024-07-13 | [41836](https://github.com/airbytehq/airbyte/pull/41836) | Update dependencies |
| 1.0.10 | 2024-07-10 | [41500](https://github.com/airbytehq/airbyte/pull/41500) | Update dependencies |
| 1.0.9 | 2024-07-09 | [41174](https://github.com/airbytehq/airbyte/pull/41174) | Update dependencies |
| 1.0.8 | 2024-07-06 | [40820](https://github.com/airbytehq/airbyte/pull/40820) | Update dependencies |
| 1.0.7 | 2024-06-27 | [40215](https://github.com/airbytehq/airbyte/pull/40215) | Replaced deprecated AirbyteLogger with logging.Logger |
| 1.0.6 | 2024-06-25 | [40474](https://github.com/airbytehq/airbyte/pull/40474) | Update dependencies |
| 1.0.5 | 2024-06-22 | [40012](https://github.com/airbytehq/airbyte/pull/40012) | Update dependencies |
| 1.0.4 | 2024-06-06 | [39178](https://github.com/airbytehq/airbyte/pull/39178) | [autopull] Upgrade base image to v1.2.2 |
| 1.0.3 | 2024-04-19 | [37246](https://github.com/airbytehq/airbyte/pull/37246) | Updating to 0.80.0 CDK |
| 1.0.2 | 2024-04-12 | [37246](https://github.com/airbytehq/airbyte/pull/37246) | schema descriptions |
| 1.0.1 | 2024-03-05 | [35828](https://github.com/airbytehq/airbyte/pull/35828) | Bump version to unarchive supportLevel in Cloud productionDB |
| 1.0.0 | 2024-03-01 | [35763](https://github.com/airbytehq/airbyte/pull/35763) | Re-introduce updated connector to catalog from archival repo |
| 0.5.0 | 2024-02-22 | [34622](https://github.com/airbytehq/airbyte/pull/34622) | Republish connector using base image/Poetry, update schemas |
| 0.4.1 | 2022-06-10 | [13685](https://github.com/airbytehq/airbyte/pull/13685) | Add state_checkpoint_interval to Recurly stream |
| 0.4.0 | 2022-01-28 | [9866](https://github.com/airbytehq/airbyte/pull/9866) | Revamp Recurly Schema and add more resources |
| 0.3.2 | 2022-01-20 | [8617](https://github.com/airbytehq/airbyte/pull/8617) | Update connector fields title/description |
| 0.3.1 | 2022-01-10 | [9382](https://github.com/airbytehq/airbyte/pull/9382) | Source Recurly: avoid loading all accounts when importing account coupon redemptions |
| 0.3.0 | 2021-12-08 | [8468](https://github.com/airbytehq/airbyte/pull/8468) | Support Incremental Sync Mode |

</details>

# Square

This page contains the setup guide and reference information for the Square source connector.

## Prerequisites

- A [Square Developer account](https://developer.squareup.com/apps) with an application created.
- A personal access token or OAuth credentials (Client ID, Client Secret, and refresh token). See [Square access tokens](https://developer.squareup.com/docs/build-basics/access-tokens) for details.

## Setup guide

### Step 1: Set up Square

1. Create a [Square Application](https://developer.squareup.com/apps).
2. Obtain a [personal access token](https://developer.squareup.com/docs/build-basics/access-tokens) or complete the [OAuth flow](https://developer.squareup.com/docs/oauth-api/create-urls-for-square-authorization) to get a Client ID, Client Secret, and refresh token.

### Step 2: Set up the Square connector in Airbyte

1. In Airbyte, navigate to **Sources** and click **+ New source**.
2. Select **Square** from the source type dropdown.
3. Choose an authentication method:
   - **API Key**: Enter the access token from your Square Application settings page (under **Credentials**).
   - **OAuth**: Enter the Client ID and Client Secret from your Square Application settings page (under **OAuth**), along with the refresh token obtained during the authorization flow.
4. Set **Sandbox** to `true` if you are using a Square sandbox environment.
5. Set a **Start Date** (UTC, format `YYYY-MM-DD`). Data before this date is not replicated.
6. Optionally enable **Include Deleted Objects** to sync deleted Items, Categories, Discounts, and Taxes.

## Supported sync modes

The Square source connector supports the following [sync modes](https://docs.airbyte.com/cloud/core-concepts#connection-sync-modes):

- [Full Refresh - Overwrite](https://docs.airbyte.com/understanding-airbyte/connections/full-refresh-overwrite/)
- [Full Refresh - Append](https://docs.airbyte.com/understanding-airbyte/connections/full-refresh-append)
- [Incremental - Append](https://docs.airbyte.com/understanding-airbyte/connections/incremental-append)
- [Incremental - Append + Deduped](https://docs.airbyte.com/understanding-airbyte/connections/incremental-append-deduped)

## Supported Streams

- [Items](https://developer.squareup.com/explorer/square/catalog-api/search-catalog-objects) (Incremental)
- [Categories](https://developer.squareup.com/explorer/square/catalog-api/search-catalog-objects) (Incremental)
- [Discounts](https://developer.squareup.com/explorer/square/catalog-api/search-catalog-objects) (Incremental)
- [Taxes](https://developer.squareup.com/explorer/square/catalog-api/search-catalog-objects) (Incremental)
- [Modifier Lists](https://developer.squareup.com/explorer/square/catalog-api/search-catalog-objects) (Incremental)
- [Payments](https://developer.squareup.com/reference/square/payments-api/list-payments) (Incremental)
- [Refunds](https://developer.squareup.com/reference/square/refunds-api/list-payment-refunds) (Incremental)
- [Orders](https://developer.squareup.com/reference/square/orders-api/search-orders) (Incremental)
- [Locations](https://developer.squareup.com/explorer/square/locations-api/list-locations)
- [Team Members](https://developer.squareup.com/reference/square/team-api/search-team-members)
- [Team Member Wages](https://developer.squareup.com/explorer/square/labor-api/list-team-member-wages)
- [Customers](https://developer.squareup.com/explorer/square/customers-api/list-customers)
- [Shifts](https://developer.squareup.com/reference/square/labor-api/search-shifts)
- [Inventory](https://developer.squareup.com/reference/square/inventory-api/batch-retrieve-inventory-counts)
- [Bank Accounts](https://developer.squareup.com/reference/square/bank-accounts-api/list-bank-accounts)
- [Cash Drawers](https://developer.squareup.com/explorer/square/cash-drawers-api/list-cash-drawer-shifts)
- [Loyalty](https://developer.squareup.com/explorer/square/loyalty-api/search-loyalty-accounts)

## Limitations and considerations

Square uses dynamic rate limiting that varies by endpoint and current API load. The connector handles `429 Too Many Requests` responses with a 30-second constant backoff before retrying. For more details, see [Square's rate limit guidance](https://developer.squareup.com/forums/t/current-square-api-rate-limit/449).

The Orders stream is partitioned by location. Each location's orders are fetched independently via the [SearchOrders](https://developer.squareup.com/reference/square/orders-api/search-orders) endpoint with a page size of 1,000 records per request.

## Useful links

- [Square API Explorer](https://developer.squareup.com/explorer/square)
- [Square API Reference](https://developer.squareup.com/reference/square)
- [Square Developer Dashboard](https://developer.squareup.com/apps)

## IP allow list

If you use Airbyte Cloud and your organization restricts access to specific IPs, add the [Airbyte Cloud IP addresses](https://docs.airbyte.com/platform/operating-airbyte/ip-allowlist) to your allow list.

## Changelog

<details>
  <summary>Expand to review</summary>

| Version | Date       | Pull Request                                             | Subject                                                                   |
| :------ | :--------- | :------------------------------------------------------- | :------------------------------------------------------------------------ |
| 1.7.21 | 2026-06-30 | [81274](https://github.com/airbytehq/airbyte/pull/81274) | Update dependencies |
| 1.7.20 | 2026-06-23 | [80667](https://github.com/airbytehq/airbyte/pull/80667) | Update dependencies |
| 1.7.19 | 2026-06-16 | [80085](https://github.com/airbytehq/airbyte/pull/80085) | Update dependencies |
| 1.7.18 | 2026-06-15 | [77704](https://github.com/airbytehq/airbyte/pull/77704) | Fix `orders` stream pagination — was silently capping at 500 records per location partition; now follows Square's `cursor` to fetch all pages |
| 1.7.17 | 2026-06-09 | [79525](https://github.com/airbytehq/airbyte/pull/79525) | Update dependencies |
| 1.7.16 | 2026-06-02 | [78955](https://github.com/airbytehq/airbyte/pull/78955) | Update dependencies |
| 1.7.15 | 2026-04-28 | [77463](https://github.com/airbytehq/airbyte/pull/77463) | Update dependencies |
| 1.7.14 | 2026-04-21 | [75866](https://github.com/airbytehq/airbyte/pull/75866) | Update dependencies |
| 1.7.13 | 2026-03-17 | [75101](https://github.com/airbytehq/airbyte/pull/75101) | Update dependencies |
| 1.7.12 | 2026-03-10 | [74570](https://github.com/airbytehq/airbyte/pull/74570) | Update dependencies |
| 1.7.11 | 2026-02-17 | [72374](https://github.com/airbytehq/airbyte/pull/72374) | Update dependencies |
| 1.7.10 | 2025-11-25 | [70017](https://github.com/airbytehq/airbyte/pull/70017) | Update dependencies |
| 1.7.9 | 2025-11-18 | [69524](https://github.com/airbytehq/airbyte/pull/69524) | Update dependencies |
| 1.7.8 | 2025-11-04 | [69161](https://github.com/airbytehq/airbyte/pull/69161) | Update dependencies |
| 1.7.7 | 2025-08-24 | [65422](https://github.com/airbytehq/airbyte/pull/65422) | Update dependencies |
| 1.7.6 | 2025-07-20 | [63672](https://github.com/airbytehq/airbyte/pull/63672) | Update dependencies |
| 1.7.5 | 2025-06-28 | [62212](https://github.com/airbytehq/airbyte/pull/62212) | Update dependencies |
| 1.7.4 | 2025-06-14 | [49109](https://github.com/airbytehq/airbyte/pull/49109) | Update dependencies |
| 1.7.3 | 2025-03-25 | [53695](https://github.com/airbytehq/airbyte/pull/53695) | fix object_types string to array |
| 1.7.3 | 2025-02-15 | [53695](https://github.com/airbytehq/airbyte/pull/53695) | Fix parameter of `categories`, `discounts`, `items`, `modifier_list` `taxes` |
| 1.7.2 | 2024-10-29 | [47869](https://github.com/airbytehq/airbyte/pull/47869) | Update dependencies |
| 1.7.1 | 2024-10-28 | [47608](https://github.com/airbytehq/airbyte/pull/47608) | Update dependencies |
| 1.7.0 | 2024-10-06 | [46527](https://github.com/airbytehq/airbyte/pull/46527) | Migrate to Manifest-only |
| 1.6.23 | 2024-10-05 | [46409](https://github.com/airbytehq/airbyte/pull/46409) | Update dependencies |
| 1.6.22 | 2024-09-28 | [46162](https://github.com/airbytehq/airbyte/pull/46162) | Update dependencies |
| 1.6.21 | 2024-09-21 | [45787](https://github.com/airbytehq/airbyte/pull/45787) | Update dependencies |
| 1.6.20 | 2024-09-14 | [45550](https://github.com/airbytehq/airbyte/pull/45550) | Update dependencies |
| 1.6.19 | 2024-09-07 | [45045](https://github.com/airbytehq/airbyte/pull/45045) | Update dependencies |
| 1.6.18 | 2024-08-24 | [44745](https://github.com/airbytehq/airbyte/pull/44745) | Update dependencies |
| 1.6.17 | 2024-08-17 | [44325](https://github.com/airbytehq/airbyte/pull/44325) | Update dependencies |
| 1.6.16 | 2024-08-12 | [43915](https://github.com/airbytehq/airbyte/pull/43915) | Update dependencies |
| 1.6.15 | 2024-08-10 | [43498](https://github.com/airbytehq/airbyte/pull/43498) | Update dependencies |
| 1.6.14 | 2024-08-03 | [43110](https://github.com/airbytehq/airbyte/pull/43110) | Update dependencies |
| 1.6.13 | 2024-07-27 | [42638](https://github.com/airbytehq/airbyte/pull/42638) | Update dependencies |
| 1.6.12 | 2024-07-20 | [42226](https://github.com/airbytehq/airbyte/pull/42226) | Update dependencies |
| 1.6.11 | 2024-07-13 | [41913](https://github.com/airbytehq/airbyte/pull/41913) | Update dependencies |
| 1.6.10 | 2024-07-10 | [41502](https://github.com/airbytehq/airbyte/pull/41502) | Update dependencies |
| 1.6.9 | 2024-07-09 | [41124](https://github.com/airbytehq/airbyte/pull/41124) | Update dependencies |
| 1.6.8 | 2024-07-06 | [40989](https://github.com/airbytehq/airbyte/pull/40989) | Update dependencies |
| 1.6.7 | 2024-06-25 | [40313](https://github.com/airbytehq/airbyte/pull/40313) | Update dependencies |
| 1.6.6 | 2024-06-22 | [40027](https://github.com/airbytehq/airbyte/pull/40027) | Update dependencies |
| 1.6.5 | 2024-06-06 | [39206](https://github.com/airbytehq/airbyte/pull/39206) | [autopull] Upgrade base image to v1.2.2 |
| 1.6.4 | 2024-06-12 | [30315](https://github.com/airbytehq/airbyte/pull/30315) | Fix `customer` stream pagination limit |
| 1.6.3 | 2024-06-14 | [39377](https://github.com/airbytehq/airbyte/pull/39377) | Add error handlers, migrate to inline schemas, move spec to manifest |
| 1.6.2 | 2024-05-03 | [37800](https://github.com/airbytehq/airbyte/pull/37800) | Migrate to Poetry. Replace custom components with default classes |
| 1.6.1 | 2023-11-07 | [31481](https://github.com/airbytehq/airbyte/pull/31481) | Fix duplicate records for `Payments` and `Refunds` stream |
| 1.6.0 | 2023-10-18 | [31115](https://github.com/airbytehq/airbyte/pull/31115) | Add `customer_id` field to `Payments` and `Orders` streams |
| 1.5.0 | 2023-10-16 | [31045](https://github.com/airbytehq/airbyte/pull/31045) | Added New Stream bank_accounts |
| 1.4.0 | 2023-10-13 | [31106](https://github.com/airbytehq/airbyte/pull/31106) | Add new stream Loyalty |
| 1.3.0 | 2023-10-12 | [31107](https://github.com/airbytehq/airbyte/pull/31107) | Add new stream Inventory |
| 1.2.0 | 2023-10-10 | [31065](https://github.com/airbytehq/airbyte/pull/31065) | Add new stream Cash drawers shifts |
| 1.1.3 | 2023-10-10 | [30960](https://github.com/airbytehq/airbyte/pull/30960) | Update `airbyte-cdk` version to `>=0.51.31` |
| 1.1.2 | 2023-07-10 | [28019](https://github.com/airbytehq/airbyte/pull/28019) | fix display order of spec fields |
| 1.1.1 | 2023-06-28 | [27762](https://github.com/airbytehq/airbyte/pull/27762) | Update following state breaking changes |
| 1.1.0 | 2023-05-24 | [26485](https://github.com/airbytehq/airbyte/pull/26485) | Remove deprecated authSpecification in favour of advancedAuth |
| 1.0.1 | 2023-05-03 | [25784](https://github.com/airbytehq/airbyte/pull/25784) | Fix Authenticator |
| 1.0.0 | 2023-05-03 | [25784](https://github.com/airbytehq/airbyte/pull/25784) | Fix Authenticator |
| 0.2.2 | 2023-03-22 | [22867](https://github.com/airbytehq/airbyte/pull/22867) | Specified date formatting in specification |
| 0.2.1 | 2023-03-06 | [23231](https://github.com/airbytehq/airbyte/pull/23231) | Publish using low-code CDK Beta version |
| 0.2.0 | 2022-11-14 | [19369](https://github.com/airbytehq/airbyte/pull/19369) | Migrate to low code (YAML); update API to version 2022-10-19; update docs |
| 0.1.4 | 2021-12-02 | [6842](https://github.com/airbytehq/airbyte/pull/6842) | Added oauth support |
| 0.1.3 | 2021-12-06 | [8425](https://github.com/airbytehq/airbyte/pull/8425) | Update title, description fields in spec |
| 0.1.2 | 2021-11-08 | [7499](https://github.com/airbytehq/airbyte/pull/7499) | Remove base-python dependencies |
| 0.1.1 | 2021-07-09 | [4645](https://github.com/airbytehq/airbyte/pull/4645) | Update \_send_request method due to Airbyte CDK changes |
| 0.1.0 | 2021-06-30 | [4439](https://github.com/airbytehq/airbyte/pull/4439) | Initial release supporting the Square API |

</details>

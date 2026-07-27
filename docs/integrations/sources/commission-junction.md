# Commission Junction (CJ Affiliate)

CJ Affiliate (formerly Commission Junction) is an affiliate marketing network. This source syncs advertiser-side commission (transaction) data from the CJ [Commission Detail GraphQL API](https://developers.cj.com/graphql/reference/Commission%20Detail).

The connector queries the `advertiserCommissions` GraphQL query, so it works only for CJ **advertiser** accounts. Publisher accounts have their own `publisherCommissions` query, which this connector doesn't support.

## Prerequisites

- A CJ advertiser account.
- A personal access token created on the [CJ Developer Portal](https://developers.cj.com/account/personal-access-tokens). Tokens are tied to the user who creates them, and the API returns data only for the companies that user has access to. Deprecated developer keys don't work with this connector.
- Your advertiser company ID (CID). This is the same value the CJ API reference calls `forAdvertisers`, and the token you use must have access to it.

## Set up the Commission Junction source

1. Sign in to the [CJ Developer Portal](https://developers.cj.com/) with your CJ account and open **Personal Access Tokens**. Create a token and copy it.
2. In Airbyte, add a new **Commission Junction (CJ Affiliate)** source and fill in the following fields.

| Field | Description |
| --- | --- |
| **Personal Access Token** | The token from step 1. Airbyte sends it as `Authorization: Bearer <token>`. |
| **CID** | Your advertiser company ID. The connector passes this as the `forAdvertisers` argument. |
| **start_date** | The earliest posting date to sync, in `YYYY-MM-DDTHH:MM:SSZ` format, for example `2025-02-01T00:00:00Z`. |

If a sync succeeds but returns no records, check that your token has access to the CID you entered. CJ answers a query whose arguments match nothing with `"count": 0` rather than an error, so a mismatched token and CID looks like an empty account.

## Supported streams

| Stream | Primary key | Sync modes |
| --- | --- | --- |
| `AdvertiserCommissions` | `commissionId` | Full refresh, Incremental |

`AdvertiserCommissions` returns one record per commission: action and order identifiers, publisher and website attribution, click and event dates, device and browser details, and commission, sale, discount, and CJ fee amounts in USD, advertiser currency, and publisher currency.

Some behaviors worth knowing before you model this data downstream:

- **All monetary values are strings.** CJ returns amounts such as `saleAmountUsd` as strings, and the connector's schema keeps them that way. Cast them in your warehouse.
- **Corrections arrive as separate delta records.** When CJ corrects or cancels a transaction, it emits a second record with the same `orderId` but a different `commissionId` and `original: false`. The correction holds the delta, not the final value, so you must sum the original and its corrections per `orderId` to get final amounts. See [Corrections](https://developers.cj.com/graphql/reference/Commission%20Detail) in the CJ reference for a worked example.
- **Item-level detail isn't synced.** The `items` field, which carries per-item quantities and amounts for advanced sale transactions, isn't part of the query the connector sends.

### Incremental syncs

The stream is incremental on `postingDate`. The connector requests one 30-day window at a time, which keeps it under the 31-day limit CJ places on date range arguments, and paginates within each window using the `sinceCommissionId` cursor until `payloadComplete` is `true`.

Each incremental sync re-reads the previous 60 days of posting dates. CJ backdates corrections and status changes onto earlier transactions, so this lookback picks up records that changed after they were first synced. Expect the connector to re-emit those records on every sync; deduplicate on `commissionId` downstream if you don't use an incremental deduped destination.

## Performance considerations

CJ enforces the following limits on the Commission Detail API, shared across everything using your token:

- 200 calls per 5 minutes.
- 120 concurrent connections.
- 10,000 commissions per response. The connector's pagination handles this.
- Date ranges of at most 31 days per query.

The connector sends up to 4 concurrent requests and retries failed requests 5 times with exponential backoff. A long backfill from an early start date issues one request per 30-day window per page, so setting `start_date` no earlier than you need keeps the first sync from bumping into the call limit.

## Changelog

<details>
  <summary>Expand to review</summary>

| Version          | Date              | Pull Request | Subject        |
|------------------|-------------------|--------------|----------------|
| 0.0.1 | 2026-07-27 | [81336](https://github.com/airbytehq/airbyte/pull/81336) | Initial release by [@Ella6882](https://github.com/Ella6882) via Connector Builder |

</details>

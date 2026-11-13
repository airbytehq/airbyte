# Commission Junction (CJ Affiliate)

CJ Affiliate is an affiliate marketing network. This connector syncs advertiser-side commissions using the [Commission Detail GraphQL API](https://developers.cj.com/graphql/reference/Commission%20Detail). It queries `advertiserCommissions`, not `publisherCommissions`.

## Set up the source

Create a personal access token on the [CJ Developer Portal](https://developers.cj.com/account/personal-access-tokens). The API uses this token to authorize access to your advertiser company ID (CID).

In Airbyte, add a **Commission Junction (CJ Affiliate)** source and configure these required fields:

| Field | Description |
| --- | --- |
| **Personal Access Token** | Your CJ personal access token, sent as a Bearer token. |
| **CID** | Your advertiser company ID, passed as `forAdvertisers` in the query. |
| **start_date** | Earliest posting date to request, in `YYYY-MM-DDTHH:MM:SSZ` format. Default: `2025-02-01T00:00:00Z`. |

If a successful sync returns no records, verify that the token has access to the configured CID and check the date range. CJ documents that unmatched query arguments, including a token/CID mismatch, can return `"count": 0` rather than an error.

## Supported streams

| Stream | Primary key | Sync modes |
| --- | --- | --- |
| `AdvertiserCommissions` | `commissionId` | Full refresh, Incremental |

The stream uses `postingDate` as its incremental cursor, requests 30-day windows, and has a configured 60-day lookback. Pagination passes `maxCommissionId` as the next `sinceCommissionId` until `payloadComplete` is `true`.

The query includes commission and sale amounts, order identifiers, and the `original` field, but not item-level `items` data. Monetary fields are nullable strings in the connector schema. For interpreting original and corrected transactions, see **Corrections** in the [CJ reference](https://developers.cj.com/graphql/reference/Commission%20Detail).

## API limits

CJ documents limits of 200 calls per 5 minutes, 120 concurrent connections, 10,000 commissions per response, and date ranges of at most 31 days per query. The connector's 30-day windows and cursor pagination accommodate the date-range and response-size limits. Its manifest configures concurrency to 4 and a maximum of 5 retries with exponential backoff.

## Changelog

<details>
  <summary>Expand to review</summary>

| Version          | Date              | Pull Request | Subject        |
|------------------|-------------------|--------------|----------------|
| 0.0.15 | 2026-11-10 | [91477](https://github.com/airbytehq/airbyte/pull/91477) | Update dependencies |
| 0.0.14 | 2026-11-03 | [90515](https://github.com/airbytehq/airbyte/pull/90515) | Update dependencies |
| 0.0.13 | 2026-10-27 | [89858](https://github.com/airbytehq/airbyte/pull/89858) | Update dependencies |
| 0.0.12 | 2026-10-20 | [89146](https://github.com/airbytehq/airbyte/pull/89146) | Update dependencies |
| 0.0.11 | 2026-10-13 | [88584](https://github.com/airbytehq/airbyte/pull/88584) | Update dependencies |
| 0.0.10 | 2026-10-06 | [87799](https://github.com/airbytehq/airbyte/pull/87799) | Update dependencies |
| 0.0.9 | 2026-09-29 | [87102](https://github.com/airbytehq/airbyte/pull/87102) | Update dependencies |
| 0.0.8 | 2026-09-22 | [86585](https://github.com/airbytehq/airbyte/pull/86585) | Update dependencies |
| 0.0.7 | 2026-09-15 | [85992](https://github.com/airbytehq/airbyte/pull/85992) | Update dependencies |
| 0.0.6 | 2026-09-08 | [85453](https://github.com/airbytehq/airbyte/pull/85453) | Update dependencies |
| 0.0.5 | 2026-08-18 | [84537](https://github.com/airbytehq/airbyte/pull/84537) | Update dependencies |
| 0.0.4 | 2026-08-11 | [83873](https://github.com/airbytehq/airbyte/pull/83873) | Update dependencies |
| 0.0.3 | 2026-08-04 | [83420](https://github.com/airbytehq/airbyte/pull/83420) | Update dependencies |
| 0.0.2 | 2026-07-28 | [82883](https://github.com/airbytehq/airbyte/pull/82883) | Update dependencies |
| 0.0.1 | 2026-07-27 | [81336](https://github.com/airbytehq/airbyte/pull/81336) | Initial release by [@Ella6882](https://github.com/Ella6882) via Connector Builder |

</details>

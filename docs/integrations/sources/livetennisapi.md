# Live Tennis API

Sync real-time tennis data from the [Live Tennis API](https://livetennisapi.com) into your data warehouse.

This source connector syncs live, upcoming, and completed matches (each with its latest score), the ranked player list, and upcoming scheduled fixtures.

Four of the five streams run on the API's self-serve FREE tier. `completed_matches` does not: it pages historical results, which the vendor sells as part of its paid History product, so it needs a BASIC or higher key. See [Plan tiers](#plan-tiers).

## Prerequisites

- A Live Tennis API key. A free key (no card required, 1,000 requests/day) is available at [livetennisapi.com/subscribe/free](https://livetennisapi.com/subscribe/free). The key is sent as the `X-API-Key` request header.
- A BASIC or higher key if you want to sync `completed_matches`. Every other stream works on the free key.

## Configuration

| Input | Type | Description | Default Value |
|-------|------|-------------|---------------|
| `api_key` | `string` | API Key. Your Live Tennis API key, sent as the `X-API-Key` request header. A free key covers every stream except `completed_matches`, which needs BASIC or higher. |  |

## Streams

| Stream Name | Primary Key | Pagination | Supports Full Sync | Supports Incremental | Minimum plan |
|-------------|-------------|------------|---------------------|----------------------|--------------|
| live_matches | id | DefaultPaginator | ✅ |  ❌  | FREE |
| upcoming_matches | id | DefaultPaginator | ✅ |  ❌  | FREE |
| completed_matches | id | DefaultPaginator | ✅ |  ❌  | BASIC |
| players | id | DefaultPaginator | ✅ |  ❌  | FREE |
| fixtures | id | DefaultPaginator | ✅ |  ❌  | FREE |

`live_matches`, `upcoming_matches` and `completed_matches` are the three lifecycle views of `GET /matches` (`status=live|upcoming|completed`). `players` and `fixtures` map to `GET /players` and `GET /fixtures`.

These endpoints expose no cursor or updated-at filter, so all streams are full refresh. Records are deduplicated on `id`.

### Plan tiers

The Live Tennis API gates access by plan (FREE / BASIC / PRO / ULTRA). `status=live` and `status=upcoming` on `GET /matches`, plus `GET /players` and `GET /fixtures`, are FREE. `status=completed` pages historical results and belongs to the paid History product, so it requires BASIC, the same rule the vendor applies to `/history/matches`.

On a free key, `completed_matches` fails the sync with `403 upgrade_required` and a typed configuration error. The other four streams are unaffected. If you are on the free plan, deselect `completed_matches` in your connection.

### Pagination

Every list endpoint accepts `limit` (default 50, maximum 200) and `offset` (default 0) and answers with `{data: [...], meta: {limit, offset, count}}`. The connector requests pages of 200 and stops when a page returns fewer than 200 records.

### Performance considerations

The FREE tier allows 30 requests/minute and 1,000/day, and paid tiers allow more. The short-window limit is surfaced through the `X-RateLimit-Limit`, `X-RateLimit-Remaining` and `X-RateLimit-Reset` response headers. On a `429` the connector waits for the number of seconds given in the `Retry-After` response header before retrying.

Timestamps are UTC ISO 8601 with a `Z` suffix.

## Limitations & Troubleshooting

- `401 unauthorized` means the key is missing, unknown, or disabled. Check the `api_key` field.
- `403 upgrade_required` means the key's plan tier does not cover the endpoint. On a free key this comes from `completed_matches`; either upgrade to BASIC or deselect the stream. A `403` on any other stream means the key has been downgraded or disabled.
- Other endpoints behind higher plan tiers (match events, market prices, model analysis, the point-by-point history tape, the 1968–2022 results archive, and the WebSocket feed) are intentionally not exposed by this connector.

## IP allow list

If you use Airbyte Cloud and your organization restricts access to specific IPs, add the [Airbyte Cloud IP addresses](https://docs.airbyte.com/platform/operating-airbyte/ip-allowlist) to your allow list.

## Changelog

<details>
  <summary>Expand to review</summary>

| Version          | Date              | Pull Request | Subject        |
|------------------|-------------------|--------------|----------------|
| 0.0.1 | 2026-07-26 | | Initial release of the Live Tennis API source connector |

</details>

# Live Tennis API

Sync real-time tennis data from the [Live Tennis API](https://livetennisapi.com) into your data warehouse.

This source connector syncs live, upcoming, and completed matches (each with its latest score), the ranked player list, and upcoming scheduled fixtures. Every stream it uses is on the API's self-serve FREE tier.

## Prerequisites

- A Live Tennis API key. A free key (no card required, 1,000 requests/day) is available at [livetennisapi.com/subscribe/free](https://livetennisapi.com/subscribe/free). The key is sent as the `X-API-Key` request header.

## Configuration

| Input | Type | Description | Default Value |
|-------|------|-------------|---------------|
| `api_key` | `string` | API Key. Your Live Tennis API key, sent as the `X-API-Key` request header. |  |

## Streams

| Stream Name | Primary Key | Pagination | Supports Full Sync | Supports Incremental |
|-------------|-------------|------------|---------------------|----------------------|
| live_matches | id | DefaultPaginator | ✅ |  ❌  |
| upcoming_matches | id | DefaultPaginator | ✅ |  ❌  |
| completed_matches | id | DefaultPaginator | ✅ |  ❌  |
| players | id | DefaultPaginator | ✅ |  ❌  |
| fixtures | id | DefaultPaginator | ✅ |  ❌  |

`live_matches`, `upcoming_matches` and `completed_matches` are the three lifecycle views of `GET /matches` (`status=live|upcoming|completed`). `players` and `fixtures` map to `GET /players` and `GET /fixtures`.

These endpoints expose no cursor or updated-at filter, so all streams are full refresh. Records are deduplicated on `id`.

### Pagination

Every list endpoint accepts `limit` (default 50, maximum 200) and `offset` (default 0) and answers with `{data: [...], meta: {limit, offset, count}}`. The connector requests pages of 200 and stops when a page returns fewer than 200 records.

### Performance considerations

The FREE tier allows 1,000 requests/day, and the API additionally applies a short-window request limit, surfaced through the `X-RateLimit-Limit`, `X-RateLimit-Remaining` and `X-RateLimit-Reset` response headers. On a `429` the connector waits for the number of seconds given in the `Retry-After` response header before retrying.

Timestamps are UTC ISO 8601 with a `Z` suffix.

## Limitations & Troubleshooting

- `401 unauthorized` means the key is missing, unknown, or disabled. Check the `api_key` field.
- `403 upgrade_required` means the key's plan tier does not unlock the endpoint. Every stream in this connector is on the FREE tier, so a `403` normally means the key has been downgraded or disabled.
- Endpoints behind higher plan tiers (match events, market prices, model analysis, historical results, and the WebSocket feed) are intentionally not exposed by this connector.

## IP allow list

If you use Airbyte Cloud and your organization restricts access to specific IPs, add the [Airbyte Cloud IP addresses](https://docs.airbyte.com/platform/operating-airbyte/ip-allowlist) to your allow list.

## Changelog

<details>
  <summary>Expand to review</summary>

| Version          | Date              | Pull Request | Subject        |
|------------------|-------------------|--------------|----------------|
| 0.0.1 | 2026-07-26 | | Initial release of the Live Tennis API source connector |

</details>

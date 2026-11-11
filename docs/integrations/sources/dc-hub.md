# DC Hub

<HideInUI>

This page contains the setup guide and reference information for the [DC Hub](https://dchub.cloud) source connector.

</HideInUI>

DC Hub (dchub.cloud): data center and energy intelligence. The Data Center Power Index (DCPI) scores 300+ markets daily on where data centers can get grid power. Also available as 94 MCP tools at https://dchub.cloud/mcp.

This connector syncs DC Hub's public REST API: DCPI market scores and verdicts, data center market inventory, US grid operator snapshots, interconnection queue projects, and data center capacity listings. The API is described at https://dchub.cloud/openapi.json.

## Prerequisites

- An API key is optional. Without one, the `dcpi_verdicts` stream is complete, most other streams return a preview, and the `grid_intelligence` stream is skipped.
- To get a key, send one POST request to `https://dchub.cloud/api/v1/keys/claim`. No account is needed. See https://dchub.cloud/developers.

## Setup guide

1. In Airbyte, add a new source and select **DC Hub**.
2. Optional: enter your DC Hub API key in **API Key**. The connector sends it as the `X-API-Key` header.
3. Optional: in **Grid operators**, choose which US grid operators (ISOs and RTOs) to sync. Leave it empty to sync all seven: PJM, ERCOT, CAISO, MISO, SPP, NYISO, and ISONE.
4. Click **Set up source**. The connection check reads the `dcpi_verdicts` stream.

## Configuration

| Input | Type | Description | Default Value |
|-------|------|-------------|---------------|
| `api_key` | `string` | API Key. Optional DC Hub API key, sent as the `X-API-Key` header. |  |
| `isos` | `array` | Grid operators. US grid operators to sync for the `grid_intelligence` and `interconnection_queue` streams. Leave empty for all seven. | PJM, ERCOT, CAISO, MISO, SPP, NYISO, ISONE |

## Supported sync modes

| Feature | Supported? |
| :--- | :--- |
| Full Refresh Sync | Yes |
| Incremental Sync | No |

Every stream is a current snapshot that DC Hub recomputes daily or more often. A daily full refresh keeps a destination current.

## Supported streams

| Stream | Endpoint | Primary key | Contents |
| :--- | :--- | :--- | :--- |
| `dcpi_scores` | `GET /api/v1/dcpi/scores` | `market_slug` | DCPI composite score, verdict, ISO, state, coordinates, and provenance for each scored market |
| `dcpi_verdicts` | `GET /api/v1/dcpi/verdicts` | `market_slug` | BUILD, CAUTION, or AVOID verdict for every DCPI market |
| `markets` | `GET /api/v1/markets` | `id` | Data center markets with their cities, facility count, and tracked power in MW |
| `grid_intelligence` | `GET /api/v1/grid/intelligence/{iso}` | `iso` | One snapshot per grid operator: demand, generation mix, installed capacity, headroom, and market prices, each with an as-of time |
| `interconnection_queue` | `GET /api/v1/interconnection-queue/refined?iso={iso}` | `queue_id` | Active interconnection queue projects: capacity, fuel, county, queue date, status, and estimated time to power |
| `capacity_listings` | `GET /api/v1/listings` | `id` | Data center capacity listed to buy or lease: powered land, powered shells, turnkey, and colocation |

## Limitations

- The `interconnection_queue` endpoint returns at most 1,000 projects per grid operator per request and doesn't page. For a grid operator with more active projects, a sync gets the first 1,000 in the API's order.
- The API decides which fields a given key receives. A field the key can't read is returned as `null`, and the record is still emitted.
- A request without a key to an endpoint that requires one gets HTTP 401, 402, or 403. The connector logs that response and skips the stream, so the rest of the sync completes.

## Data and attribution

Each record keeps the `as_of`, `computed_at`, or provenance fields that DC Hub returns. Cite DC Hub (dchub.cloud) with the as-of date when you publish a figure. Terms for current DCPI values: https://dchub.cloud/terms#dcpi-current-data.

## Changelog

<details>
  <summary>Expand to review</summary>

| Version | Date | Pull Request | Subject |
| :--- | :--- | :--- | :--- |
| 0.0.1 | 2026-11-11 | [92006](https://github.com/airbytehq/airbyte/pull/92006) | Initial release by [@azmartone67](https://github.com/azmartone67) via Connector Builder |

</details>

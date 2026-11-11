# DC Hub
DC Hub (dchub.cloud): data center and energy intelligence. The Data Center Power Index (DCPI) scores 300+ markets daily on where data centers can get grid power. Also available as 94 MCP tools at https://dchub.cloud/mcp.

## Configuration

| Input | Type | Description | Default Value |
|-------|------|-------------|---------------|
| `isos` | `array` | Grid operators. US grid operators (ISOs/RTOs) to sync for the grid_intelligence and interconnection_queue streams. Leave empty for all seven. | [PJM, ERCOT, CAISO, MISO, SPP, NYISO, ISONE] |
| `api_key` | `string` | API Key. Optional DC Hub API key, sent as the X-API-Key header. Without one, most streams return a preview and grid_intelligence is skipped. Get a key with one POST to https://dchub.cloud/api/v1/keys/claim (no account needed), or see https://dchub.cloud/developers. |  |

## Streams
| Stream Name | Primary Key | Pagination | Supports Full Sync | Supports Incremental |
|-------------|-------------|------------|---------------------|----------------------|
| dcpi_scores | market_slug | No pagination | ✅ |  ❌  |
| dcpi_verdicts | market_slug | No pagination | ✅ |  ❌  |
| markets | id | No pagination | ✅ |  ❌  |
| grid_intelligence | iso | No pagination | ✅ |  ❌  |
| interconnection_queue | queue_id | No pagination | ✅ |  ❌  |
| capacity_listings | id | No pagination | ✅ |  ❌  |

## Changelog

<details>
  <summary>Expand to review</summary>

| Version          | Date              | Pull Request | Subject        |
|------------------|-------------------|--------------|----------------|
| 0.0.1 | 2026-11-11 | | Initial release by [@azmartone67](https://github.com/azmartone67) via Connector Builder |

</details>

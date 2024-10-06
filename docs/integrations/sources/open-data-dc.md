# Open Data DC
Open Data DC source connector which ingests data from the MAR 2 API.
The District of Columbia government uses the Master Address Repository (MAR) to implement intelligent search functionality for finding and verifying addresses, place names, blocks and intersections.
More information can be found here https://developers.data.dc.gov/

## Configuration

| Input | Type | Description | Default Value |
|-------|------|-------------|---------------|
| `api_key` | `string` | API Key.  |  |
| `location` | `string` | location. address or place or block |  |
| `marid` | `string` | marid. A unique identifier (Master Address Repository). |  |

## Streams
| Stream Name | Primary Key | Pagination | Supports Full Sync | Supports Incremental |
|-------------|-------------|------------|---------------------|----------------------|
| locations |  | No pagination | ✅ |  ❌  |
| units | UnitNum | No pagination | ✅ |  ❌  |
| ssls | SSL | No pagination | ✅ |  ❌  |

## Changelog

<details>
  <summary>Expand to review</summary>

| Version          | Date              | Pull Request | Subject        |
|------------------|-------------------|--------------|----------------|
| 0.0.1 | 2024-10-06 | | Initial release by [@aazam-gh](https://github.com/aazam-gh) via Connector Builder |

</details>

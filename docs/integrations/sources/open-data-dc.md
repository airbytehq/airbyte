# Open Data DC

Open Data DC source connector which ingests data from the MAR 2 API.

## Prerequisites

Create a developer MAR account at https://developers.data.dc.gov/ to obtain your API key.

The MAR 2 API allows users to search for addresses, place names, blocks and intersections within the DC boundary.
In order to use this search, input the string in the `location` field.

MARID is the Master Address Repository ID associated with all addresses within the DC boundary. 

## Set up the Adjust source connector

1. Click **Sources** and then click **+ New source**.
2. On the Set up the source page, select **Open Data DC** from the Source type dropdown.
3. Enter a name for your new source.
4. For **API Key**, enter your API key obtained in the previous step.
5. For **location**, enter any string to search for a location as explained in the previous step.
6. For **marid**, enter your MARID as explained in the previous step.
7. Click **Set up source**.

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

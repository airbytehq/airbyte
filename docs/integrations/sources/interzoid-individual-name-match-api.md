# Interzoid Individual Name Match API
This API provides a powerful mechanism for matching similar individual/person names within or across various data sources and datasets. It works by generating a similarity key using AI and specialized algorithms, so variations of the same name (variations, typos, nicknames) generate the same similarity key (John Smith, Jon Smith, Jonathan Smyth, etc.). Data can then be matched based on similarity key rather than the organization name data itself for dramatically higher match rates.

## Configuration

| Input | Type | Description | Default Value |
|-------|------|-------------|---------------|
| `api_key` | `string` | API Key.  |  |

## Streams
| Stream Name | Primary Key | Pagination | Supports Full Sync | Supports Incremental |
|-------------|-------------|------------|---------------------|----------------------|
| simkey |  | No pagination | ✅ |  ❌  |

## Changelog

<details>
  <summary>Expand to review</summary>

| Version          | Date              | Pull Request | Subject        |
|------------------|-------------------|--------------|----------------|
| 0.0.1 | 2025-11-18 | | Initial release by [@interzoid](https://github.com/interzoid) via Connector Builder |

</details>

# Standardize Company Names API
This API standardizes/normalizes organization and company names into their official name standard using an advanced &#39;closest match&#39; AI algorithm. It handles various input variations including abbreviations, alternate spellings, and multiple languages, converting them all to standardized English equivalents. Perfect for data cleansing, analytics/reporting, and maintaining consistent organization records across your data assets and systems.

## Configuration

| Input | Type | Description | Default Value |
|-------|------|-------------|---------------|
| `api_key` | `string` | API Key.  |  |

## Streams
| Stream Name | Primary Key | Pagination | Supports Full Sync | Supports Incremental |
|-------------|-------------|------------|---------------------|----------------------|
| standard |  | No pagination | ✅ |  ❌  |

## Changelog

<details>
  <summary>Expand to review</summary>

| Version          | Date              | Pull Request | Subject        |
|------------------|-------------------|--------------|----------------|
| 0.0.1 | 2025-11-18 | | Initial release by [@interzoid](https://github.com/interzoid) via Connector Builder |

</details>

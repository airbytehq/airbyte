# Interzoid
Interzoid is an AI-powered API platform providing data quality, data matching, and data enrichment capabilities that help Airbyte pipelines deliver higher data ROI. This connector enables you to call Interzoid’s APIs directly from your Airbyte workflows to match records, enrich attributes, normalize and standardize fields, or verify data as part of your extraction and loading processes. The result is cleaner, more consistent, and more actionable datasets flowing through your Airbyte integrations—without additional engineering overhead.

## Configuration

| Input | Type | Description | Default Value |
|-------|------|-------------|---------------|
| `api_key` | `string` | API Key.  |  |

## Streams
| Stream Name | Primary Key | Pagination | Supports Full Sync | Supports Incremental |
|-------------|-------------|------------|---------------------|----------------------|
| Company Name Matching |  | No pagination | ✅ |  ❌  |
| Individual Name Matching |  | No pagination | ✅ |  ❌  |
| Street Address Matching |  | No pagination | ✅ |  ❌  |
| Standardize Company Names |  | No pagination | ✅ |  ❌  |

## Changelog

<details>
  <summary>Expand to review</summary>

| Version          | Date              | Pull Request | Subject        |
|------------------|-------------------|--------------|----------------|
| 0.0.1 | 2025-11-24 | | Initial release by [@interzoid](https://github.com/interzoid) via Connector Builder |

</details>

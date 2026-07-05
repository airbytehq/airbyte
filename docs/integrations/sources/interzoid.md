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

## IP allow list

If you use Airbyte Cloud and your organization restricts access to specific IPs, add the [Airbyte Cloud IP addresses](https://docs.airbyte.com/platform/operating-airbyte/ip-allowlist) to your allow list.

## Changelog

<details>
  <summary>Expand to review</summary>

| Version          | Date              | Pull Request | Subject        |
|------------------|-------------------|--------------|----------------|
| 0.0.7 | 2026-06-30 | [81124](https://github.com/airbytehq/airbyte/pull/81124) | Update dependencies |
| 0.0.6 | 2026-06-23 | [80522](https://github.com/airbytehq/airbyte/pull/80522) | Update dependencies |
| 0.0.5 | 2026-06-16 | [79902](https://github.com/airbytehq/airbyte/pull/79902) | Update dependencies |
| 0.0.4 | 2026-06-09 | [79369](https://github.com/airbytehq/airbyte/pull/79369) | Update dependencies |
| 0.0.3 | 2026-06-02 | [78764](https://github.com/airbytehq/airbyte/pull/78764) | Update dependencies |
| 0.0.2 | 2026-04-28 | [77278](https://github.com/airbytehq/airbyte/pull/77278) | Update dependencies |
| 0.0.1 | 2025-11-24 | | Initial release by [@interzoid](https://github.com/interzoid) via Connector Builder |

</details>

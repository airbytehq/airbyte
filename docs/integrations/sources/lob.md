# Lob
This page contains the setup guide and reference information for the [Lob](https://dashboard.lob.com/) source connector.

## Documentation reference:
Visit `https://docs.lob.com/` for API documentation

## Authentication setup
`Lob` uses Basic Http authentication via api key, Visit `https://dashboard.lob.com/settings/api-keys` for getting your api keys. Refer `https://docs.lob.com/#tag/Authentication` for more details.

## Configuration

| Input | Type | Description | Default Value |
|-------|------|-------------|---------------|
| `api_key` | `string` | API Key. API key to use for authentication. You can find your account&#39;s API keys in your Dashboard Settings at https://dashboard.lob.com/settings/api-keys. |  |
| `start_date` | `string` | Start date.  |  |
| `limit` | `string` | Limit. Max records per page limit | 50 |

## Streams
| Stream Name | Primary Key | Pagination | Supports Full Sync | Supports Incremental |
|-------------|-------------|------------|---------------------|----------------------|
| addresses | id | DefaultPaginator | ✅ |  ✅  |
| banks | id | DefaultPaginator | ✅ |  ✅  |
| postcards | id | DefaultPaginator | ✅ |  ✅  |
| templates | id | DefaultPaginator | ✅ |  ✅  |
| templates_versions | id | DefaultPaginator | ✅ |  ✅  |
| campaigns | id | DefaultPaginator | ✅ |  ✅  |
| uploads | id | DefaultPaginator | ✅ |  ✅  |
| qr_code_analytics | resource_id | DefaultPaginator | ✅ |  ✅  |

## Changelog

<details>
  <summary>Expand to review</summary>

| Version | Date | Pull Request | Subject |
| ------------------ | ------------ | --- | ---------------- |
| 0.0.18 | 2025-03-08 | [55443](https://github.com/airbytehq/airbyte/pull/55443) | Update dependencies |
| 0.0.17 | 2025-03-01 | [54803](https://github.com/airbytehq/airbyte/pull/54803) | Update dependencies |
| 0.0.16 | 2025-02-22 | [54348](https://github.com/airbytehq/airbyte/pull/54348) | Update dependencies |
| 0.0.15 | 2025-02-15 | [53862](https://github.com/airbytehq/airbyte/pull/53862) | Update dependencies |
| 0.0.14 | 2025-02-08 | [53268](https://github.com/airbytehq/airbyte/pull/53268) | Update dependencies |
| 0.0.13 | 2025-02-01 | [52774](https://github.com/airbytehq/airbyte/pull/52774) | Update dependencies |
| 0.0.12 | 2025-01-25 | [52224](https://github.com/airbytehq/airbyte/pull/52224) | Update dependencies |
| 0.0.11 | 2025-01-18 | [51843](https://github.com/airbytehq/airbyte/pull/51843) | Update dependencies |
| 0.0.10 | 2025-01-11 | [51166](https://github.com/airbytehq/airbyte/pull/51166) | Update dependencies |
| 0.0.9 | 2024-12-28 | [50662](https://github.com/airbytehq/airbyte/pull/50662) | Update dependencies |
| 0.0.8 | 2024-12-21 | [50070](https://github.com/airbytehq/airbyte/pull/50070) | Update dependencies |
| 0.0.7 | 2024-12-14 | [49602](https://github.com/airbytehq/airbyte/pull/49602) | Update dependencies |
| 0.0.6 | 2024-12-12 | [49269](https://github.com/airbytehq/airbyte/pull/49269) | Update dependencies |
| 0.0.5 | 2024-12-11 | [48899](https://github.com/airbytehq/airbyte/pull/48899) | Starting with this version, the Docker image is now rootless. Please note that this and future versions will not be compatible with Airbyte versions earlier than 0.64 |
| 0.0.4 | 2024-11-04 | [48226](https://github.com/airbytehq/airbyte/pull/48226) | Update dependencies |
| 0.0.3 | 2024-10-29 | [47867](https://github.com/airbytehq/airbyte/pull/47867) | Update dependencies |
| 0.0.2 | 2024-10-28 | [47627](https://github.com/airbytehq/airbyte/pull/47627) | Update dependencies |
| 0.0.1 | 2024-09-22 | [45843](https://github.com/airbytehq/airbyte/pull/45843) | Initial release by [@btkcodedev](https://github.com/btkcodedev) via Connector Builder |

</details>

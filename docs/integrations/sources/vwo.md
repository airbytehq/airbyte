# VWO
This directory contains the manifest-only connector for [`source-vwo`](https://app.vwo.com/).

## Documentation reference:
Visit `https://developers.vwo.com/reference/introduction-1` for API documentation

## Authentication setup
`VWO` uses API token authentication, Visit `https://app.vwo.com/#/developers/tokens` for getting your api token. Refer `https://developers.vwo.com/reference/authentication-for-personal-use-of-api-1`.

## Configuration

| Input | Type | Description | Default Value |
|-------|------|-------------|---------------|
| `api_key` | `string` | API Key.  |  |
| `start_date` | `string` | Start date.  |  |

## Streams
| Stream Name | Primary Key | Pagination | Supports Full Sync | Supports Incremental |
|-------------|-------------|------------|---------------------|----------------------|
| accounts | id | DefaultPaginator | ✅ |  ✅  |
| accounts_feeds | id | DefaultPaginator | ✅ |  ✅  |
| users | id | DefaultPaginator | ✅ |  ✅  |
| smartcode | uid | DefaultPaginator | ✅ |  ❌  |
| campaigns | id | DefaultPaginator | ✅ |  ✅  |
| custom_widgets | id | DefaultPaginator | ✅ |  ✅  |
| thresholds | uid | DefaultPaginator | ✅ |  ❌  |
| integrations | uid | DefaultPaginator | ✅ |  ❌  |
| labels | id | DefaultPaginator | ✅ |  ❌  |

## Changelog

<details>
  <summary>Expand to review</summary>

| Version | Date | Pull Request | Subject |
| ------------------ | ------------ | --- | ---------------- |
| 0.0.7 | 2025-01-11 | [51395](https://github.com/airbytehq/airbyte/pull/51395) | Update dependencies |
| 0.0.6 | 2024-12-28 | [50798](https://github.com/airbytehq/airbyte/pull/50798) | Update dependencies |
| 0.0.5 | 2024-12-21 | [50314](https://github.com/airbytehq/airbyte/pull/50314) | Update dependencies |
| 0.0.4 | 2024-12-14 | [49767](https://github.com/airbytehq/airbyte/pull/49767) | Update dependencies |
| 0.0.3 | 2024-12-12 | [49411](https://github.com/airbytehq/airbyte/pull/49411) | Update dependencies |
| 0.0.2 | 2024-10-29 | [47475](https://github.com/airbytehq/airbyte/pull/47475) | Update dependencies |
| 0.0.1 | 2024-09-23 | [45851](https://github.com/airbytehq/airbyte/pull/45851) | Initial release by [@btkcodedev](https://github.com/btkcodedev) via Connector Builder |

</details>

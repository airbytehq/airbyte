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
| 0.0.1 | 2024-09-23 | [45851](https://github.com/airbytehq/airbyte/pull/45851) | Initial release by [@btkcodedev](https://github.com/btkcodedev) via Connector Builder |

</details>
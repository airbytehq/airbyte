# Poplar
Website: https://app.heypoplar.com/
Documentation: https://developers.heypoplar.com/

## Configuration

| Input | Type | Description | Default Value |
|-------|------|-------------|---------------|
| `access_token` | `string` | Access Token. Your Poplar API Access Token. Generate it from the [API Credentials page](https://app.heypoplar.com/credentials) in your account. Use a production token for live data or a test token for testing purposes. |  |

## Streams
| Stream Name | Primary Key | Pagination | Supports Full Sync | Supports Incremental |
|-------------|-------------|------------|---------------------|----------------------|
| campaigns | id | No pagination | ✅ |  ❌  |
| creatives |  | No pagination | ✅ |  ❌  |
| audiences | id | No pagination | ✅ |  ❌  |
| me | id | No pagination | ✅ |  ❌  |
| mailings | id | No pagination | ✅ |  ❌  |

## Changelog

<details>
  <summary>Expand to review</summary>

| Version          | Date              | Pull Request | Subject        |
|------------------|-------------------|--------------|----------------|
| 0.0.2 | 2025-04-05 | [57291](https://github.com/airbytehq/airbyte/pull/57291) | Update dependencies |
| 0.0.1 | 2025-03-31 | | Initial release by [@btkcodedev](https://github.com/btkcodedev) via Connector Builder |

</details>

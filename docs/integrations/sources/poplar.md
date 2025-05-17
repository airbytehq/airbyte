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
| 0.0.8 | 2025-05-17 | [60546](https://github.com/airbytehq/airbyte/pull/60546) | Update dependencies |
| 0.0.7 | 2025-05-10 | [60110](https://github.com/airbytehq/airbyte/pull/60110) | Update dependencies |
| 0.0.6 | 2025-05-04 | [59522](https://github.com/airbytehq/airbyte/pull/59522) | Update dependencies |
| 0.0.5 | 2025-04-27 | [59048](https://github.com/airbytehq/airbyte/pull/59048) | Update dependencies |
| 0.0.4 | 2025-04-19 | [58469](https://github.com/airbytehq/airbyte/pull/58469) | Update dependencies |
| 0.0.3 | 2025-04-12 | [57910](https://github.com/airbytehq/airbyte/pull/57910) | Update dependencies |
| 0.0.2 | 2025-04-05 | [57291](https://github.com/airbytehq/airbyte/pull/57291) | Update dependencies |
| 0.0.1 | 2025-03-31 | | Initial release by [@btkcodedev](https://github.com/btkcodedev) via Connector Builder |

</details>

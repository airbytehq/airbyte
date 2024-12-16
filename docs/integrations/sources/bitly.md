# Bitly
Bitly is the most widely trusted link management platform in the world. By using the Bitly API, you will exercise the full power of your links through automated link customization, mobile deep linking, and click analytics.

## Configuration

| Input | Type | Description | Default Value |
|-------|------|-------------|---------------|
| `api_key` | `string` | API Key.  |  |
| `start_date` | `string` | Start date.  |  |
| `end_date` | `string` | End date.  |  |

Generate API Key [here](https://app.bitly.com/settings/api/) or go to Settings → Developer settings → API → Access token and click Generate token. See [here](https://dev.bitly.com/docs/getting-started/authentication/) for more details. 

## Streams
| Stream Name | Primary Key | Pagination | Supports Full Sync | Supports Incremental |
|-------------|-------------|------------|---------------------|----------------------|
| bitlinks | id | DefaultPaginator | ✅ |  ✅  |
| bitlink_clicks |  | No pagination | ✅ |  ❌  |
| bsds |  | No pagination | ✅ |  ❌  |
| campaigns | guid | No pagination | ✅ |  ✅  |
| channels | guid | No pagination | ✅ |  ✅  |
| groups | guid | No pagination | ✅ |  ✅  |
| group_preferences | group_guid | No pagination | ✅ |  ❌  |
| group_shorten_counts |  | No pagination | ✅ |  ❌  |
| organizations | guid | No pagination | ✅ |  ✅  |
| organization_shorten_counts |  | No pagination | ✅ |  ❌  |
| qr_codes | id | No pagination | ✅ |  ✅  |

## Changelog

<details>
  <summary>Expand to review</summary>

| Version | Date | Pull Request | Subject |
|---------|------|--------------|---------|
| 0.0.5 | 2024-12-14 | [49571](https://github.com/airbytehq/airbyte/pull/49571) | Update dependencies |
| 0.0.4 | 2024-12-12 | [49005](https://github.com/airbytehq/airbyte/pull/49005) | Update dependencies |
| 0.0.3 | 2024-11-04 | [48171](https://github.com/airbytehq/airbyte/pull/48171) | Update dependencies |
| 0.0.2 | 2024-10-28 | [47516](https://github.com/airbytehq/airbyte/pull/47516) | Update dependencies |
| 0.0.1 | 2024-09-01 | | Initial release by [@topefolorunso](https://github.com/topefolorunso) via Connector Builder |

</details>

# Smartwaiver
The Smartwaiver connector for Airbyte enables seamless integration with the Smartwaiver API, allowing users to automate the extraction of waiver-related data. Smartwaiver is a platform that digitizes waivers, converting them into customizable, legally-binding documents with signatures.

## Configuration

| Input | Type | Description | Default Value |
|-------|------|-------------|---------------|
| `api_key` | `string` | API Key. You can retrieve your token by visiting your dashboard then click on My Account then click on API keys. |  |
| `start_date` | `string` | Start Date.  | 2017-01-24 13:12:29 |

## Streams

:::warning

Due to some limitation of SmartWaiver API it can have situations where you won't be able to retrieve all records available.

:::

| Stream Name | Primary Key | Pagination | Supports Full Sync | Supports Incremental |
|-------------|-------------|------------|---------------------|----------------------|
| templates | templateId | No pagination | ✅ |  ❌  |
| signed_waivers | waiverId | DefaultPaginator | ✅ |  ❌  |
| detailed_signed_waiver | waiverId | No pagination | ✅ |  ❌  |
| checkins | waiverId | DefaultPaginator | ✅ |  ❌  |

## Changelog

<details>
  <summary>Expand to review</summary>

| Version          | Date              | Pull Request | Subject        |
|------------------|-------------------|--------------|----------------|
| 0.0.2 | 2024-10-29 | [47825](https://github.com/airbytehq/airbyte/pull/47825) | Update dependencies |
| 0.0.1 | 2024-10-09 | | Initial release by [@avirajsingh7](https://github.com/avirajsingh7) via Connector Builder |

</details>

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
| 0.0.12 | 2025-02-08 | [53538](https://github.com/airbytehq/airbyte/pull/53538) | Update dependencies |
| 0.0.11 | 2025-02-01 | [53105](https://github.com/airbytehq/airbyte/pull/53105) | Update dependencies |
| 0.0.10 | 2025-01-25 | [52390](https://github.com/airbytehq/airbyte/pull/52390) | Update dependencies |
| 0.0.9 | 2025-01-18 | [51989](https://github.com/airbytehq/airbyte/pull/51989) | Update dependencies |
| 0.0.8 | 2025-01-11 | [51378](https://github.com/airbytehq/airbyte/pull/51378) | Update dependencies |
| 0.0.7 | 2024-12-28 | [50757](https://github.com/airbytehq/airbyte/pull/50757) | Update dependencies |
| 0.0.6 | 2024-12-21 | [50304](https://github.com/airbytehq/airbyte/pull/50304) | Update dependencies |
| 0.0.5 | 2024-12-14 | [49732](https://github.com/airbytehq/airbyte/pull/49732) | Update dependencies |
| 0.0.4 | 2024-12-12 | [49435](https://github.com/airbytehq/airbyte/pull/49435) | Update dependencies |
| 0.0.3 | 2024-12-11 | [49117](https://github.com/airbytehq/airbyte/pull/49117) | Starting with this version, the Docker image is now rootless. Please note that this and future versions will not be compatible with Airbyte versions earlier than 0.64 |
| 0.0.2 | 2024-10-29 | [47825](https://github.com/airbytehq/airbyte/pull/47825) | Update dependencies |
| 0.0.1 | 2024-10-09 | | Initial release by [@avirajsingh7](https://github.com/avirajsingh7) via Connector Builder |

</details>

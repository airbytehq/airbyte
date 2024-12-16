# SavvyCal
Sync your scheduled meetings and scheduling links from SavvyCal!

## Configuration

| Input | Type | Description | Default Value |
|-------|------|-------------|---------------|
| `api_key` | `string` | API Key. Go to SavvyCal → Settings → Developer → Personal Tokens and make a new token. Then, copy the private key. https://savvycal.com/developers |  |

## Streams
| Stream Name | Primary Key | Pagination | Supports Full Sync | Supports Incremental |
|-------------|-------------|------------|---------------------|----------------------|
| events | id | DefaultPaginator | ✅ |  ❌  |
| scheduling_links | id | DefaultPaginator | ✅ |  ❌  |
| timezones | id | No pagination | ✅ |  ❌  |

## Changelog

<details>
  <summary>Expand to review</summary>

| Version | Date | Pull Request | Subject |
|---------|------|--------------|---------|
| 0.0.6 | 2024-12-14 | [49688](https://github.com/airbytehq/airbyte/pull/49688) | Update dependencies |
| 0.0.5 | 2024-12-12 | [49342](https://github.com/airbytehq/airbyte/pull/49342) | Update dependencies |
| 0.0.4 | 2024-12-11 | [49044](https://github.com/airbytehq/airbyte/pull/49044) | Starting with this version, the Docker image is now rootless. Please note that this and future versions will not be compatible with Airbyte versions earlier than 0.64 |
| 0.0.3 | 2024-11-04 | [47816](https://github.com/airbytehq/airbyte/pull/47816) | Update dependencies |
| 0.0.2 | 2024-10-28 | [47558](https://github.com/airbytehq/airbyte/pull/47558) | Update dependencies |
| 0.0.1 | 2024-09-01 | | Initial release by [@natikgadzhi](https://github.com/natikgadzhi) via Connector Builder |

</details>

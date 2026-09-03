# smsmode SMS
A source connector for the smsmode API dedicated to standard SMS services, supporting message logs and general consumption data synchronization.

## Configuration

| Input | Type | Description | Default Value |
|-------|------|-------------|---------------|
| `api_key` | `string` | API Key. Your smsmode API key. You can generate and manage API keys in the smsmode dashboard under the &#39;Credentials&#39; section: https://dev.smsmode.com/commons/v1/#tag/Credential. Make sure the key is active and has the required permissions for your use case. |  |

## Streams
| Stream Name | Primary Key | Pagination | Supports Full Sync | Supports Incremental |
|-------------|-------------|------------|---------------------|----------------------|
| messages |  | DefaultPaginator | ✅ |  ❌  |
| consumptions | consumptionId | DefaultPaginator | ✅ |  ❌  |

## Changelog

<details>
  <summary>Expand to review</summary>

| Version          | Date              | Pull Request | Subject        |
|------------------|-------------------|--------------|----------------|
| 0.0.1 | 2026-06-15 | | Initial release by [@CaladeTechnologies](https://github.com/CaladeTechnologies) via Connector Builder |

</details>

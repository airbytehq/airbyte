# ZapSign
Website: https://app.zapsign.co/
API Reference: https://docs.zapsign.com.br/

## Configuration

| Input | Type | Description | Default Value |
|-------|------|-------------|---------------|
| `api_token` | `string` | API Token. Your static API token for authentication. You can find it in your ZapSign account under the &#39;Settings&#39; or &#39;API&#39; section. For more details, refer to the [Getting Started](https://docs.zapsign.com.br/english/getting-started#how-do-i-get-my-api-token) guide. |  |
| `start_date` | `string` | Start date.  |  |
| `signer_ids` | `array` | Signer IDs. The signer ids for signer stream |  |

## Streams
| Stream Name | Primary Key | Pagination | Supports Full Sync | Supports Incremental |
|-------------|-------------|------------|---------------------|----------------------|
| templates | token | DefaultPaginator | ✅ |  ✅  |
| documents | token | DefaultPaginator | ✅ |  ✅  |
| signer | token | DefaultPaginator | ✅ |  ❌  |

## Changelog

<details>
  <summary>Expand to review</summary>

| Version          | Date              | Pull Request | Subject        |
|------------------|-------------------|--------------|----------------|
| 0.0.9 | 2025-06-15 | [61228](https://github.com/airbytehq/airbyte/pull/61228) | Update dependencies |
| 0.0.8 | 2025-05-24 | [60739](https://github.com/airbytehq/airbyte/pull/60739) | Update dependencies |
| 0.0.7 | 2025-05-10 | [59999](https://github.com/airbytehq/airbyte/pull/59999) | Update dependencies |
| 0.0.6 | 2025-05-04 | [59551](https://github.com/airbytehq/airbyte/pull/59551) | Update dependencies |
| 0.0.5 | 2025-04-26 | [58947](https://github.com/airbytehq/airbyte/pull/58947) | Update dependencies |
| 0.0.4 | 2025-04-19 | [58552](https://github.com/airbytehq/airbyte/pull/58552) | Update dependencies |
| 0.0.3 | 2025-04-13 | [58037](https://github.com/airbytehq/airbyte/pull/58037) | Update dependencies |
| 0.0.2 | 2025-04-05 | [57383](https://github.com/airbytehq/airbyte/pull/57383) | Update dependencies |
| 0.0.1 | 2025-04-04 | [57008](https://github.com/airbytehq/airbyte/pull/57008) | Initial release by [@btkcodedev](https://github.com/btkcodedev) via Connector Builder |

</details>

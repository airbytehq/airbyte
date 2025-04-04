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
| 0.0.1 | 2025-04-04 | | Initial release by [@btkcodedev](https://github.com/btkcodedev) via Connector Builder |

</details>

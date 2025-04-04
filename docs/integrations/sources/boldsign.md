# BoldSign
Website: https://app.boldsign.com/
API Reference: https://developers.boldsign.com/api-overview/getting-started/?region=us

## Configuration

| Input | Type | Description | Default Value |
|-------|------|-------------|---------------|
| `api_key` | `string` | API Key. Your BoldSign API key. You can generate it by navigating to the API menu in the BoldSign app, selecting &#39;API Key&#39;, and clicking &#39;Generate API Key&#39;. Copy the generated key and paste it here. |  |
| `start_date` | `string` | Start date.  |  |

## Streams
| Stream Name | Primary Key | Pagination | Supports Full Sync | Supports Incremental |
|-------------|-------------|------------|---------------------|----------------------|
| documents | documentId | DefaultPaginator | ✅ |  ✅  |
| brands | brandId | DefaultPaginator | ✅ |  ❌  |
| senderIdentities | email | DefaultPaginator | ✅ |  ❌  |
| teams | teamId | DefaultPaginator | ✅ |  ✅  |
| templates | documentId | DefaultPaginator | ✅ |  ✅  |
| users_list | userId | DefaultPaginator | ✅ |  ✅  |
| custom_fields | customFieldId | DefaultPaginator | ✅ |  ❌  |
| contacts | id | DefaultPaginator | ✅ |  ❌  |

## Changelog

<details>
  <summary>Expand to review</summary>

| Version          | Date              | Pull Request | Subject        |
|------------------|-------------------|--------------|----------------|
| 0.0.1 | 2025-04-04 | | Initial release by [@btkcodedev](https://github.com/btkcodedev) via Connector Builder |

</details>

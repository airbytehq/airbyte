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
| 0.0.7 | 2025-05-17 | [59840](https://github.com/airbytehq/airbyte/pull/59840) | Update dependencies |
| 0.0.6 | 2025-05-03 | [59345](https://github.com/airbytehq/airbyte/pull/59345) | Update dependencies |
| 0.0.5 | 2025-04-26 | [58724](https://github.com/airbytehq/airbyte/pull/58724) | Update dependencies |
| 0.0.4 | 2025-04-19 | [58240](https://github.com/airbytehq/airbyte/pull/58240) | Update dependencies |
| 0.0.3 | 2025-04-12 | [57617](https://github.com/airbytehq/airbyte/pull/57617) | Update dependencies |
| 0.0.2 | 2025-04-05 | [57159](https://github.com/airbytehq/airbyte/pull/57159) | Update dependencies |
| 0.0.1 | 2025-04-04 | [57005](https://github.com/airbytehq/airbyte/pull/57005) | Initial release by [@btkcodedev](https://github.com/btkcodedev) via Connector Builder |

</details>

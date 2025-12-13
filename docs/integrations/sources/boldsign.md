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
| 0.0.20 | 2025-12-09 | [70661](https://github.com/airbytehq/airbyte/pull/70661) | Update dependencies |
| 0.0.19 | 2025-11-25 | [69948](https://github.com/airbytehq/airbyte/pull/69948) | Update dependencies |
| 0.0.18 | 2025-11-18 | [69463](https://github.com/airbytehq/airbyte/pull/69463) | Update dependencies |
| 0.0.17 | 2025-10-29 | [68697](https://github.com/airbytehq/airbyte/pull/68697) | Update dependencies |
| 0.0.16 | 2025-10-21 | [68221](https://github.com/airbytehq/airbyte/pull/68221) | Update dependencies |
| 0.0.15 | 2025-10-14 | [67834](https://github.com/airbytehq/airbyte/pull/67834) | Update dependencies |
| 0.0.14 | 2025-10-07 | [67211](https://github.com/airbytehq/airbyte/pull/67211) | Update dependencies |
| 0.0.13 | 2025-09-30 | [65632](https://github.com/airbytehq/airbyte/pull/65632) | Update dependencies |
| 0.0.12 | 2025-08-09 | [64656](https://github.com/airbytehq/airbyte/pull/64656) | Update dependencies |
| 0.0.11 | 2025-07-12 | [63033](https://github.com/airbytehq/airbyte/pull/63033) | Update dependencies |
| 0.0.10 | 2025-07-05 | [62531](https://github.com/airbytehq/airbyte/pull/62531) | Update dependencies |
| 0.0.9 | 2025-06-28 | [62138](https://github.com/airbytehq/airbyte/pull/62138) | Update dependencies |
| 0.0.8 | 2025-06-21 | [61875](https://github.com/airbytehq/airbyte/pull/61875) | Update dependencies |
| 0.0.7 | 2025-06-15 | [59840](https://github.com/airbytehq/airbyte/pull/59840) | Update dependencies |
| 0.0.6 | 2025-05-03 | [59345](https://github.com/airbytehq/airbyte/pull/59345) | Update dependencies |
| 0.0.5 | 2025-04-26 | [58724](https://github.com/airbytehq/airbyte/pull/58724) | Update dependencies |
| 0.0.4 | 2025-04-19 | [58240](https://github.com/airbytehq/airbyte/pull/58240) | Update dependencies |
| 0.0.3 | 2025-04-12 | [57617](https://github.com/airbytehq/airbyte/pull/57617) | Update dependencies |
| 0.0.2 | 2025-04-05 | [57159](https://github.com/airbytehq/airbyte/pull/57159) | Update dependencies |
| 0.0.1 | 2025-04-04 | [57005](https://github.com/airbytehq/airbyte/pull/57005) | Initial release by [@btkcodedev](https://github.com/btkcodedev) via Connector Builder |

</details>

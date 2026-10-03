# OneFlow
OneFlow is a contract management and automation platform. This connector syncs data from your OneFlow instance, including users, contacts, contracts, templates, template types, workspaces, contract events, contract data fields, and contract parties.

## Configuration

| Input | Type | Description | Default Value |
|-------|------|-------------|---------------|
| `api_token` | `string` | API Token. Your OneFlow API token (generate in Marketplace > API tokens) |  |

## Streams
| Stream Name | Primary Key | Pagination | Supports Full Sync | Supports Incremental |
|-------------|-------------|------------|---------------------|----------------------|
| users | id | OffsetIncrement | ✅ | ❌ |
| workspaces | id | OffsetIncrement | ✅ | ❌ |
| contacts | id | OffsetIncrement | ✅ | ❌ |
| contracts | id | OffsetIncrement | ✅ | ❌ |
| templates | id | OffsetIncrement | ✅ | ❌ |
| template_types | id | OffsetIncrement | ✅ | ❌ |
| contract_events | id | No pagination | ✅ | ❌ |
| contract_data_fields | id | No pagination | ✅ | ❌ |
| contract_parties | id | No pagination | ✅ | ❌ |

## Changelog

<details>
  <summary>Expand to review</summary>

| Version          | Date              | Pull Request | Subject        |
|------------------|-------------------|--------------|----------------|
| 0.0.1 | 2026-03-25 | | Initial release by [@t-m-v](https://github.com/t-m-v) via Connector Builder |

</details>

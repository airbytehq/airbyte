# Cloze
Cloze is a CRM tool.
Docs : https://api.cloze.com/api-docs/#!/Get_Started/get_v1_profile

## Configuration

| Input | Type | Description | Default Value |
|-------|------|-------------|---------------|
| `api_key` | `string` | API Key.  |  |
| `email` | `string` | Email.  |  |

## Streams
| Stream Name | Primary Key | Pagination | Supports Full Sync | Supports Incremental |
|-------------|-------------|------------|---------------------|----------------------|
| segments |  | No pagination | ✅ |  ❌  |
| custom_fields |  | No pagination | ✅ |  ❌  |
| people_stages |  | No pagination | ✅ |  ❌  |
| project_segments |  | No pagination | ✅ |  ❌  |
| project_stages |  | No pagination | ✅ |  ❌  |
| steps |  | No pagination | ✅ |  ❌  |
| views |  | No pagination | ✅ |  ❌  |
| team_members |  | No pagination | ✅ |  ❌  |
| team_roles |  | No pagination | ✅ |  ❌  |
| people |  | DefaultPaginator | ✅ |  ❌  |

## Changelog

<details>
  <summary>Expand to review</summary>

| Version          | Date              | Pull Request | Subject        |
|------------------|-------------------|--------------|----------------|
| 0.0.1 | 2024-10-31 | | Initial release by [@ombhardwajj](https://github.com/ombhardwajj) via Connector Builder |

</details>

# StackHawk
Website: https://www.stackhawk.com/
API Reference: https://apidocs.stackhawk.com/reference/getalertmessages

## Configuration

| Input | Type | Description | Default Value |
|-------|------|-------------|---------------|
| `api_key` | `string` | API Key. API Key could be found at `https://app.stackhawk.com/settings/apikeys` |  |
| `start_date` | `string` | Start date.  |  |

## Streams
| Stream Name | Primary Key | Pagination | Supports Full Sync | Supports Incremental |
|-------------|-------------|------------|---------------------|----------------------|
| user | stackhawkId | No pagination | ✅ |  ✅  |
| organization_members | stackhawkId | DefaultPaginator | ✅ |  ✅  |
| user_organizations | org_id | No pagination | ✅ |  ✅  |
| organization_audit | id | DefaultPaginator | ✅ |  ✅  |
| organization_teams | id | DefaultPaginator | ✅ |  ❌  |
| applications | applicationId | DefaultPaginator | ✅ |  ❌  |
| environments | environmentId | DefaultPaginator | ✅ |  ❌  |

## Changelog

<details>
  <summary>Expand to review</summary>

| Version          | Date              | Pull Request | Subject        |
|------------------|-------------------|--------------|----------------|
| 0.0.1 | 2025-04-06 | [57491](https://github.com/airbytehq/airbyte/pull/57491) | Initial release by [@btkcodedev](https://github.com/btkcodedev) via Connector Builder |

</details>

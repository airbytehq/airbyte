# SignNow
Website: https://app.signnow.com/
API Reference: https://docs.signnow.com/docs/signnow/welcome

## Configuration

| Input | Type | Description | Default Value |
|-------|------|-------------|---------------|
| `start_date` | `string` | Start date.  |  |
| `api_key` | `string` | API Key.  |  |

## Streams
| Stream Name | Primary Key | Pagination | Supports Full Sync | Supports Incremental |
|-------------|-------------|------------|---------------------|----------------------|
| user | id | No pagination | ✅ |  ✅  |
| user_modified_documents | id | No pagination | ✅ |  ✅  |
| user_documents | id | No pagination | ✅ |  ✅  |
| crm_contacts | id | DefaultPaginator | ✅ |  ✅  |
| favourites | id | DefaultPaginator | ✅ |  ❌  |
| logs | uuid | DefaultPaginator | ✅ |  ✅  |
| folder | id | DefaultPaginator | ✅ |  ✅  |
| teams | id | DefaultPaginator | ✅ |  ✅  |
| team_admins | uuid | DefaultPaginator | ✅ |  ✅  |
| brands | unique_id | DefaultPaginator | ✅ |  ❌  |
| crm_users | id | DefaultPaginator | ✅ |  ❌  |
| crm_groups | id | DefaultPaginator | ✅ |  ✅  |

## Changelog

<details>
  <summary>Expand to review</summary>

| Version          | Date              | Pull Request | Subject        |
|------------------|-------------------|--------------|----------------|
| 0.0.1 | 2025-04-02 | | Initial release by [@btkcodedev](https://github.com/btkcodedev) via Connector Builder |

</details>

# Gorgias
Website: https://gorgias.com/
API docs: https://developers.gorgias.com/reference/introduction
Auth docs: https://developers.gorgias.com/reference/authentication
API Keys: https://testerstoreusedbytester.gorgias.com/app/settings/api

## Configuration

| Input | Type | Description | Default Value |
|-------|------|-------------|---------------|
| `username` | `string` | Username.  |  |
| `password` | `string` | Password.  |  |
| `domain_name` | `string` | Domain name. Domain name given for gorgias, found as your url prefix for accessing your website |  |
| `start_date` | `string` | Start date.  |  |

## Streams
| Stream Name | Primary Key | Pagination | Supports Full Sync | Supports Incremental |
|-------------|-------------|------------|---------------------|----------------------|
| account | domain | No pagination | ✅ |  ✅  |
| customers | id | DefaultPaginator | ✅ |  ✅  |
| custom-fields | id | DefaultPaginator | ✅ |  ✅  |
| events | id | DefaultPaginator | ✅ |  ✅  |
| integrations | id | DefaultPaginator | ✅ |  ✅  |
| jobs | id | DefaultPaginator | ✅ |  ✅  |
| macros | id | DefaultPaginator | ✅ |  ✅  |
| views | id | DefaultPaginator | ✅ |  ✅  |
| rules | id | DefaultPaginator | ✅ |  ✅  |
| satisfaction-surveys | id | DefaultPaginator | ✅ |  ✅  |
| tags | id | DefaultPaginator | ✅ |  ✅  |
| teams | id | DefaultPaginator | ✅ |  ✅  |
| tickets | id | DefaultPaginator | ✅ |  ✅  |
| messages | id | DefaultPaginator | ✅ |  ✅  |
| users | id | DefaultPaginator | ✅ |  ✅  |
| views_items | id | DefaultPaginator | ✅ |  ✅  |

## Changelog

<details>
  <summary>Expand to review</summary>

| Version          | Date       | Subject        |
|------------------|------------|----------------|
| 0.0.1 | 2024-09-29 | Initial release by [@btkcodedev](https://github.com/btkcodedev) via Connector Builder|

</details>
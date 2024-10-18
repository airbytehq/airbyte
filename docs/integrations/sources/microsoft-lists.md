# Microsoft Lists
Microsoft Lists connector enables seamless data integration and synchronization between Microsoft Lists and other destination. The connector leverages Microsoft Graph API to retrieve list items efficiently, ensuring smooth workflows and real-time data accessibility

## Configuration

| Input | Type | Description | Default Value |
|-------|------|-------------|---------------|
| `site_id` | `string` | Site Id.  |  |
| `client_id` | `string` | Client ID.  |  |
| `client_secret` | `string` | Client secret.  |  |
| `application_id_uri` | `string` | Application Id URI.  |  |
| `tenant_id` | `string` | Tenant Id.  |  |
| `domain` | `string` | Domain.  |  |

## Streams
| Stream Name | Primary Key | Pagination | Supports Full Sync | Supports Incremental |
|-------------|-------------|------------|---------------------|----------------------|
| lists | id | DefaultPaginator | ✅ |  ❌  |
| listcontenttypes | id | DefaultPaginator | ✅ |  ❌  |
| listitems |  | DefaultPaginator | ✅ |  ❌  |
| items |  | DefaultPaginator | ✅ |  ❌  |
| columnvalues | id | DefaultPaginator | ✅ |  ❌  |

## Changelog

<details>
  <summary>Expand to review</summary>

| Version          | Date              | Pull Request | Subject        |
|------------------|-------------------|--------------|----------------|
| 0.0.1 | 2024-10-18 | | Initial release by [@bishalbera](https://github.com/bishalbera) via Connector Builder |

</details>

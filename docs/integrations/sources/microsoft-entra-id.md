# Microsoft Entra Id
The Microsoft Entra ID Connector for Airbyte allows seamless integration with Microsoft Entra ID, enabling secure and automated data synchronization of identity and access management information. With this connector, users can efficiently retrieve and manage user, group, and directory data to streamline identity workflows and ensure up-to-date access control within their applications.

## Configuration

| Input | Type | Description | Default Value |
|-------|------|-------------|---------------|
| `type` | `string` | Type.  |  |
| `client_id` | `string` | Client ID.  |  |
| `client_secret` | `string` | Client secret.  |  |
| `tenant_id` | `string` | Tenant Id.  |  |
| `application_id_uri` | `string` | Application Id URI.  |  |
| `user_id` | `string` | User Id.  |  |
| `ids` | `array` | Ids.  |  |
| `types` | `array` | Types.  |  |

## Streams
| Stream Name | Primary Key | Pagination | Supports Full Sync | Supports Incremental |
|-------------|-------------|------------|---------------------|----------------------|
| users | id | DefaultPaginator | ✅ |  ❌  |
| groups | id | DefaultPaginator | ✅ |  ❌  |
| applications | id | No pagination | ✅ |  ❌  |
| user_owned_deleted_items | id | DefaultPaginator | ✅ |  ❌  |
| directoryroles | id | No pagination | ✅ |  ❌  |
| auditlogs |  | DefaultPaginator | ✅ |  ❌  |
| directoryobjects | id | DefaultPaginator | ✅ |  ❌  |
| directoryroletemplates | id | DefaultPaginator | ✅ |  ❌  |
| directoryaudits |  | DefaultPaginator | ✅ |  ❌  |
| serviceprincipals | id | DefaultPaginator | ✅ |  ❌  |
| identityproviders |  | DefaultPaginator | ✅ |  ❌  |
| adminconsentrequestpolicy |  | DefaultPaginator | ✅ |  ❌  |

## Changelog

<details>
  <summary>Expand to review</summary>

| Version          | Date              | Pull Request | Subject        |
|------------------|-------------------|--------------|----------------|
| 0.0.1 | 2024-10-13 | | Initial release by [@bishalbera](https://github.com/bishalbera) via Connector Builder |

</details>

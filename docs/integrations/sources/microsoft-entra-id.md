# Microsoft Entra Id

The Microsoft Entra ID Connector for Airbyte allows seamless integration with Microsoft Entra ID, enabling secure and automated data synchronization of identity and access management information. With this connector, users can efficiently retrieve and manage user, group, and directory data to streamline identity workflows and ensure up-to-date access control within their applications.

## Authentication

First of all you need to register an application in the Microsoft Entra Admin Center. Please folow [these](https://learn.microsoft.com/en-us/graph/auth-register-app-v2) steps to do so. After that you need to follow [these](https://learn.microsoft.com/en-us/graph/auth-v2-service?context=graph%2Fapi%2F1.0&view=graph-rest-1.0&tabs=http) steps to configure the api with right permissions and get the access token.

## Configuration

| Input           | Type     | Description      | Default Value |
| --------------- | -------- | ---------------- | ------------- |
| `client_id`     | `string` | Client ID.       |               |
| `client_secret` | `string` | Client secret.   |               |
| `tenant_id`     | `string` | Tenant Id.       |               |
| `user_id`       | `string` | ID of the owner. |               |

## Streams

| Stream Name               | Primary Key | Pagination       | Supports Full Sync | Supports Incremental |
| ------------------------- | ----------- | ---------------- | ------------------ | -------------------- |
| users                     | id          | DefaultPaginator | ✅                 | ❌                   |
| groups                    | id          | DefaultPaginator | ✅                 | ❌                   |
| applications              | id          | DefaultPaginator | ✅                 | ❌                   |
| user_owned_deleted_items  | id          | DefaultPaginator | ✅                 | ❌                   |
| directoryroles            | id          | No pagination    | ✅                 | ❌                   |
| directoryroletemplates    | id          | No pagination    | ✅                 | ❌                   |
| directoryaudits           | id          | DefaultPaginator | ✅                 | ❌                   |
| serviceprincipals         | id          | DefaultPaginator | ✅                 | ❌                   |
| identityproviders         |             | DefaultPaginator | ✅                 | ❌                   |
| adminconsentrequestpolicy |             | DefaultPaginator | ✅                 | ❌                   |

## Changelog

<details>
  <summary>Expand to review</summary>

| Version | Date       | Pull Request                                             | Subject                                                                               |
| ------- | ---------- | -------------------------------------------------------- | ------------------------------------------------------------------------------------- |
| 0.0.11 | 2025-02-22 | [54355](https://github.com/airbytehq/airbyte/pull/54355) | Update dependencies |
| 0.0.10 | 2025-02-15 | [51193](https://github.com/airbytehq/airbyte/pull/51193) | Update dependencies |
| 0.0.9 | 2024-12-28 | [50630](https://github.com/airbytehq/airbyte/pull/50630) | Update dependencies |
| 0.0.8 | 2024-12-21 | [50133](https://github.com/airbytehq/airbyte/pull/50133) | Update dependencies |
| 0.0.7 | 2024-12-14 | [49596](https://github.com/airbytehq/airbyte/pull/49596) | Update dependencies |
| 0.0.6 | 2024-12-12 | [49270](https://github.com/airbytehq/airbyte/pull/49270) | Update dependencies |
| 0.0.5 | 2024-12-11 | [48941](https://github.com/airbytehq/airbyte/pull/48941) | Starting with this version, the Docker image is now rootless. Please note that this and future versions will not be compatible with Airbyte versions earlier than 0.64 |
| 0.0.4 | 2024-10-31 | [47997](https://github.com/airbytehq/airbyte/pull/47997) | Remove `audit_logs` and update auth remove `application_id_uri` parameter |
| 0.0.3 | 2024-10-29 | [47892](https://github.com/airbytehq/airbyte/pull/47892) | Update dependencies |
| 0.0.2 | 2024-10-28 | [47479](https://github.com/airbytehq/airbyte/pull/47479) | Update dependencies |
| 0.0.1   | 2024-10-18 |                                                          | Initial release by [@bishalbera](https://github.com/bishalbera) via Connector Builder |

</details>

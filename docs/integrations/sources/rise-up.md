# Rise Up
Rise Up API

## Configuration

| Input | Type | Description | Default Value |
|-------|------|-------------|---------------|
| `start_date` | `string` | Start date.  |  |
| `client_id` | `string` | Client ID.  |  |
| `client_secret` | `string` | Client secret.  |  |

## Streams
| Stream Name | Primary Key | Pagination | Supports Full Sync | Supports Incremental |
|-------------|-------------|------------|---------------------|----------------------|
| users | id | DefaultPaginator | ✅ |  ✅  |
| customfields | id | DefaultPaginator | ✅ |  ❌  |
| groups | id | DefaultPaginator | ✅ |  ✅  |
| learning_paths | id | DefaultPaginator | ✅ |  ✅  |
| learning_path_registrations | id | DefaultPaginator | ✅ |  ✅  |
| courses | id | DefaultPaginator | ✅ |  ✅  |
| course_registrations | id | DefaultPaginator | ✅ |  ✅  |
| certificates | id | DefaultPaginator | ✅ |  ✅  |
| certificate_user | idcertificate | DefaultPaginator | ✅ |  ❌  |
| certifications | iduser.idtrainingsubscription.certificationdate | DefaultPaginator | ✅ |  ❌  |
| classroom_session_registrations | id | DefaultPaginator | ✅ |  ✅  |
| skills | id | DefaultPaginator | ✅ |  ✅  |
| training_categories | id | DefaultPaginator | ✅ |  ❌  |
| classroom_sessions | id | DefaultPaginator | ✅ |  ✅  |
| modules | id | DefaultPaginator | ✅ |  ✅  |
| user_step_states | id | DefaultPaginator | ✅ |  ✅  |

## Changelog

<details>
  <summary>Expand to review</summary>

| Version          | Date              | Pull Request | Subject        |
|------------------|-------------------|--------------|----------------|
| 0.0.1 | 2025-09-18 | | Initial release by [@KimPlv](https://github.com/KimPlv) via Connector Builder |

</details>

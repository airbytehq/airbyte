# Concord
This is the setup guide for the Concord source connector.

## Configuration

| Input | Type | Description | Default Value |
|-------|------|-------------|---------------|
| `api_key` | `string` | API Key.  |  |

## Streams
| Stream Name | Primary Key | Pagination | Supports Full Sync | Supports Incremental |
|-------------|-------------|------------|---------------------|----------------------|
| people |  | DefaultPaginator | ✅ |  ❌  |
| schedules | id | No pagination | ✅ |  ❌  |
| campaigns | id | No pagination | ✅ |  ❌  |
| lists | id | No pagination | ✅ |  ❌  |
| templates | id | No pagination | ✅ |  ❌  |
| blacklisted_domains |  | No pagination | ✅ |  ❌  |
| email_accounts | id | No pagination | ✅ |  ❌  |

## Changelog

<details>
  <summary>Expand to review</summary>

| Version          | Date              | Pull Request | Subject        |
|------------------|-------------------|--------------|----------------|
| 0.0.1 | 2024-10-05 | | Initial release by [@aazam-gh](https://github.com/aazam-gh) via Connector Builder |

</details>

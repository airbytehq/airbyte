# Missive
This page contains the setup guide and reference information for the [Missive](https://missiveapp.com/) source connector.

## Documentation reference:
Visit `https://missiveapp.com/help/api-documentation/rest-endpoints` for API documentation

## Authentication setup
`Missive` uses Bearer token authentication authentication, Visit your profile settings for getting your api keys. Refer `https://missiveapp.com/help/api-documentation/getting-started` for more details.

## Configuration

| Input | Type | Description | Default Value |
|-------|------|-------------|---------------|
| `api_key` | `string` | API Key.  |  |
| `limit` | `string` | Limit. Max records per page limit | 50 |
| `start_date` | `string` | Start date.  |  |
| `kind` | `string` | Kind. Kind parameter for `contact_groups` stream | group |

## Streams
| Stream Name | Primary Key | Pagination | Supports Full Sync | Supports Incremental |
|-------------|-------------|------------|---------------------|----------------------|
| contact_books | id | DefaultPaginator | ✅ |  ❌  |
| contacts | id | DefaultPaginator | ✅ |  ✅  |
| contact_groups | id | DefaultPaginator | ✅ |  ❌  |
| users | id | DefaultPaginator | ✅ |  ❌  |
| teams | id | DefaultPaginator | ✅ |  ❌  |
| shared_labels | id | DefaultPaginator | ✅ |  ❌  |
| organizations | id | DefaultPaginator | ✅ |  ❌  |
| conversations | id | No pagination | ✅ |  ✅  |

## Changelog

<details>
  <summary>Expand to review</summary>

| Version | Date | Pull Request | Subject |
| ------------------ | ------------ | --- | ---------------- |
| 0.0.1 | 2024-09-22 | [45844](https://github.com/airbytehq/airbyte/pull/45844) | Initial release by [@btkcodedev](https://github.com/btkcodedev) via Connector Builder |

</details>
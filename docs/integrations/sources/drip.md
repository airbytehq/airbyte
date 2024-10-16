# Drip
Integrate seamlessly with Drip using this Airbyte connector, enabling smooth data sync for all your email marketing needs. Effortlessly connect and automate data flows to optimize your marketing strategies with ease

## Configuration

| Input | Type | Description | Default Value |
|-------|------|-------------|---------------|
| `api_key` | `string` | API Key. API key to use. Find it at https://www.getdrip.com/user/edit |  |

## Streams
| Stream Name | Primary Key | Pagination | Supports Full Sync | Supports Incremental |
|-------------|-------------|------------|---------------------|----------------------|
| accounts | id | DefaultPaginator | ✅ |  ❌  |
| broadcasts | id | DefaultPaginator | ✅ |  ❌  |
| campaigns | id | DefaultPaginator | ✅ |  ❌  |
| users | email | DefaultPaginator | ✅ |  ❌  |
| workflows | id | DefaultPaginator | ✅ |  ❌  |
| subscribers | id | DefaultPaginator | ✅ |  ❌  |
| custom_fields | custom_field_identifiers | DefaultPaginator | ✅ |  ❌  |
| conversions | id | DefaultPaginator | ✅ |  ❌  |
| events | account_id | DefaultPaginator | ✅ |  ❌  |
| tags | tags | DefaultPaginator | ✅ |  ❌  |
| webhooks | id | DefaultPaginator | ✅ |  ❌  |

## Changelog

<details>
  <summary>Expand to review</summary>

| Version          | Date              | Pull Request | Subject        |
|------------------|-------------------|--------------|----------------|
| 0.0.1 | 2024-10-08 | | Initial release by [@parthiv11](https://github.com/parthiv11) via Connector Builder |

</details>

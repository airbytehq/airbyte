# Tinyemail
Tinyemail is an email marketing tool.
We can extract data from campaigns and contacts streams using this connector.
[API Docs](https://docs.tinyemail.com/docs/tiny-email/tinyemail)

## Configuration

| Input | Type | Description | Default Value |
|-------|------|-------------|---------------|
| `api_key` | `string` | API Key.  |  |

## Streams
| Stream Name | Primary Key | Pagination | Supports Full Sync | Supports Incremental |
|-------------|-------------|------------|---------------------|----------------------|
| campaigns | id | DefaultPaginator | ✅ |  ❌  |
| contacts | id | No pagination | ✅ |  ❌  |
| sender_details | id | No pagination | ✅ |  ❌  |
| contact_members |  | DefaultPaginator | ✅ |  ❌  |

## Changelog

<details>
  <summary>Expand to review</summary>

| Version          | Date              | Pull Request | Subject        |
|------------------|-------------------|--------------|----------------|
| 0.0.1 | 2024-11-08 | | Initial release by [@ombhardwajj](https://github.com/ombhardwajj) via Connector Builder |

</details>

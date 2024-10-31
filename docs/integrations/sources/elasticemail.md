# Elasticemail
Elasticemail is an email delivery and marketing platform.
Using this connector we extract data from streams such as campaigns , contacts , lists and statistics!
Docs : https://elasticemail.com/developers/api-documentation/rest-api

## Configuration

| Input | Type | Description | Default Value |
|-------|------|-------------|---------------|
| `from` | `string` | From.  |  |
| `api_key` | `string` | API Key.  |  |
| `scope_type` | `string` | scope type.  |  |

## Streams
| Stream Name | Primary Key | Pagination | Supports Full Sync | Supports Incremental |
|-------------|-------------|------------|---------------------|----------------------|
| campaigns |  | DefaultPaginator | ✅ |  ❌  |
| contacts |  | DefaultPaginator | ✅ |  ❌  |
| events |  | DefaultPaginator | ✅ |  ❌  |
| files |  | DefaultPaginator | ✅ |  ❌  |
| inboundroute |  | No pagination | ✅ |  ❌  |
| lists |  | DefaultPaginator | ✅ |  ❌  |
| segments |  | DefaultPaginator | ✅ |  ❌  |
| statistics |  | DefaultPaginator | ✅ |  ❌  |
| templates |  | DefaultPaginator | ✅ |  ❌  |

## Changelog

<details>
  <summary>Expand to review</summary>

| Version          | Date              | Pull Request | Subject        |
|------------------|-------------------|--------------|----------------|
| 0.0.1 | 2024-10-31 | | Initial release by [@ombhardwajj](https://github.com/ombhardwajj) via Connector Builder |

</details>

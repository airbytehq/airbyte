# Perigon
Website: https://www.perigon.io/
API Reference: https://docs.perigon.io/reference/all-news

## Configuration

| Input | Type | Description | Default Value |
|-------|------|-------------|---------------|
| `api_key` | `string` | API Key. Your API key for authenticating with the Perigon API. Obtain it by creating an account at https://www.perigon.io/sign-up and verifying your email. The API key will be visible on your account dashboard. |  |
| `start_date` | `string` | Start date.  |  |

## Streams
| Stream Name | Primary Key | Pagination | Supports Full Sync | Supports Incremental |
|-------------|-------------|------------|---------------------|----------------------|
| articles | articleId | DefaultPaginator | ✅ |  ✅  |
| stories | id | DefaultPaginator | ✅ |  ✅  |
| journalists | id | No pagination | ✅ |  ✅  |
| sources | id | No pagination | ✅ |  ✅  |
| people | wikidataId | No pagination | ✅ |  ✅  |
| companies | id | No pagination | ✅ |  ✅  |
| topics | id | DefaultPaginator | ✅ |  ✅  |

## Changelog

<details>
  <summary>Expand to review</summary>

| Version          | Date              | Pull Request | Subject        |
|------------------|-------------------|--------------|----------------|
| 0.0.3 | 2025-04-19 | [58522](https://github.com/airbytehq/airbyte/pull/58522) | Update dependencies |
| 0.0.2 | 2025-04-12 | [57891](https://github.com/airbytehq/airbyte/pull/57891) | Update dependencies |
| 0.0.1 | 2025-04-06 | [57494](https://github.com/airbytehq/airbyte/pull/57494) | Initial release by [@btkcodedev](https://github.com/btkcodedev) via Connector Builder |

</details>

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
| 0.0.12 | 2025-08-02 | [64182](https://github.com/airbytehq/airbyte/pull/64182) | Update dependencies |
| 0.0.11 | 2025-07-26 | [63839](https://github.com/airbytehq/airbyte/pull/63839) | Update dependencies |
| 0.0.10 | 2025-07-19 | [63422](https://github.com/airbytehq/airbyte/pull/63422) | Update dependencies |
| 0.0.9 | 2025-07-12 | [63167](https://github.com/airbytehq/airbyte/pull/63167) | Update dependencies |
| 0.0.8 | 2025-07-05 | [62578](https://github.com/airbytehq/airbyte/pull/62578) | Update dependencies |
| 0.0.7 | 2025-06-28 | [62326](https://github.com/airbytehq/airbyte/pull/62326) | Update dependencies |
| 0.0.6 | 2025-06-21 | [61873](https://github.com/airbytehq/airbyte/pull/61873) | Update dependencies |
| 0.0.5 | 2025-06-14 | [60076](https://github.com/airbytehq/airbyte/pull/60076) | Update dependencies |
| 0.0.4 | 2025-05-03 | [59090](https://github.com/airbytehq/airbyte/pull/59090) | Update dependencies |
| 0.0.3 | 2025-04-19 | [58522](https://github.com/airbytehq/airbyte/pull/58522) | Update dependencies |
| 0.0.2 | 2025-04-12 | [57891](https://github.com/airbytehq/airbyte/pull/57891) | Update dependencies |
| 0.0.1 | 2025-04-06 | [57494](https://github.com/airbytehq/airbyte/pull/57494) | Initial release by [@btkcodedev](https://github.com/btkcodedev) via Connector Builder |

</details>

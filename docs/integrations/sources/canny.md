# Canny
A manifest only source for Canny. https://canny.io/

## Configuration

| Input | Type | Description | Default Value |
|-------|------|-------------|---------------|
| `api_key` | `string` | API Key. You can find your secret API key in Your Canny Subdomain &gt; Settings &gt; API |  |

## Streams
| Stream Name | Primary Key | Pagination | Supports Full Sync | Supports Incremental |
|-------------|-------------|------------|---------------------|----------------------|
| boards | id | No pagination | ✅ |  ❌  |
| categories | id | DefaultPaginator | ✅ |  ❌  |
| changelog_entries | id | DefaultPaginator | ✅ |  ❌  |
| comments | id | DefaultPaginator | ✅ |  ❌  |
| companies | id | DefaultPaginator | ✅ |  ❌  |
| posts | id | DefaultPaginator | ✅ |  ❌  |
| status_changes | id | DefaultPaginator | ✅ |  ❌  |
| tags | id | DefaultPaginator | ✅ |  ❌  |
| users | id | DefaultPaginator | ✅ |  ❌  |
| votes | id | DefaultPaginator | ✅ |  ❌  |

## Changelog

<details>
  <summary>Expand to review</summary>

| Version | Date       | Pull Request                                             | Subject                                                                                   |
|---------|------------|----------------------------------------------------------|-------------------------------------------------------------------------------------------|
| 0.0.1   | 2024-09-15 | [45588](https://github.com/airbytehq/airbyte/pull/45588) | Initial release by [@pabloescoder](https://github.com/pabloescoder) via Connector Builder |

</details>
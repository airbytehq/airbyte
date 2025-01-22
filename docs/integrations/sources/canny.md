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
| 0.0.9 | 2025-01-18 | [51765](https://github.com/airbytehq/airbyte/pull/51765) | Update dependencies |
| 0.0.8 | 2025-01-11 | [51237](https://github.com/airbytehq/airbyte/pull/51237) | Update dependencies |
| 0.0.7 | 2024-12-28 | [50489](https://github.com/airbytehq/airbyte/pull/50489) | Update dependencies |
| 0.0.6 | 2024-12-21 | [50171](https://github.com/airbytehq/airbyte/pull/50171) | Update dependencies |
| 0.0.5 | 2024-12-14 | [49574](https://github.com/airbytehq/airbyte/pull/49574) | Update dependencies |
| 0.0.4 | 2024-12-12 | [49013](https://github.com/airbytehq/airbyte/pull/49013) | Update dependencies |
| 0.0.3 | 2024-11-04 | [48235](https://github.com/airbytehq/airbyte/pull/48235) | Update dependencies |
| 0.0.2 | 2024-10-29 | [47727](https://github.com/airbytehq/airbyte/pull/47727) | Update dependencies |
| 0.0.1 | 2024-09-15 | [45588](https://github.com/airbytehq/airbyte/pull/45588) | Initial release by [@pabloescoder](https://github.com/pabloescoder) via Connector Builder |

</details>

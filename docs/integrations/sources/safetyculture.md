# SafetyCulture
Setup guide for safetyculture source &lt;wip&gt;

## Configuration

| Input | Type | Description | Default Value |
|-------|------|-------------|---------------|
| `api_key` | `string` | API Key.  |  |

## Streams
| Stream Name | Primary Key | Pagination | Supports Full Sync | Supports Incremental |
|-------------|-------------|------------|---------------------|----------------------|
| feed_users | id | DefaultPaginator | ✅ |  ❌  |
| groups | id | No pagination | ✅ |  ❌  |
| connections | id | No pagination | ✅ |  ❌  |
| heads_up | id | DefaultPaginator | ✅ |  ❌  |
| assets | id | DefaultPaginator | ✅ |  ❌  |
| folders | id | DefaultPaginator | ✅ |  ❌  |
| global_response_sets | responseset_id | No pagination | ✅ |  ❌  |
| schedule_items | id | DefaultPaginator | ✅ |  ❌  |
| actions |  | DefaultPaginator | ✅ |  ❌  |
| templates | template_id | No pagination | ✅ |  ❌  |
| feed_templates | id | DefaultPaginator | ✅ |  ❌  |

## Changelog

<details>
  <summary>Expand to review</summary>

| Version          | Date              | Pull Request | Subject        |
|------------------|-------------------|--------------|----------------|
| 0.0.1 | 2024-10-04 | | Initial release by [@aazam-gh](https://github.com/aazam-gh) via Connector Builder |

</details>

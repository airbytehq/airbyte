# Height
New source: Height
API Documentation: https://height.notion.site/API-documentation-643aea5bf01742de9232e5971cb4afda
Website: https://height.app
Access key docs: https://height.notion.site/OAuth-Apps-on-Height-a8ebeab3f3f047e3857bd8ce60c2f640

## Configuration

| Input | Type | Description | Default Value |
|-------|------|-------------|---------------|
| `api_key` | `string` | API Key.  |  |
| `start_date` | `string` | Start date.  |  |
| `search_query` | `string` | search_query. Search query to be used with search stream | task |

## Streams
| Stream Name | Primary Key | Pagination | Supports Full Sync | Supports Incremental |
|-------------|-------------|------------|---------------------|----------------------|
| workspace | id | No pagination | ✅ |  ✅  |
| lists | id | No pagination | ✅ |  ✅  |
| tasks | id | No pagination | ✅ |  ✅  |
| activities | id | No pagination | ✅ |  ✅  |
| field_templates | id | No pagination | ✅ |  ❌  |
| users | id | No pagination | ✅ |  ✅  |
| groups | id | No pagination | ✅ |  ✅  |
| search | id | No pagination | ✅ |  ✅  |

## Changelog

<details>
  <summary>Expand to review</summary>

| Version          | Date       | Subject        |
|------------------|------------|----------------|
| 0.0.1 | 2024-08-31 | Initial release by [@btkcodedev](https://github.com/btkcodedev) via Connector Builder|

</details>
# Wufoo
The Airbyte connector for [Wufoo](https://www.wufoo.com/) enables seamless data integration between Wufoo and various destinations. It extracts form entries, form metadata, and user information from Wufoo via the Wufoo API. This connector helps automate the synchronization of survey and form data with your chosen data warehouse or analytical tools, simplifying data-driven insights and reporting.

## Configuration

| Input | Type | Description | Default Value |
|-------|------|-------------|---------------|
| `api_key` | `string` | API Key. Your Wufoo API Key. You can find it by logging into your Wufoo account, selecting &#39;API Information&#39; from the &#39;More&#39; dropdown on any form, and locating the 16-digit code. |  |
| `subdomain` | `string` | Subdomain. Your account subdomain/username for Wufoo. |  |

## Streams
| Stream Name | Primary Key | Pagination | Supports Full Sync | Supports Incremental |
|-------------|-------------|------------|---------------------|----------------------|
| forms | Hash | No pagination | ✅ |  ❌  |
| form_comments | CommentId | DefaultPaginator | ✅ |  ❌  |
| form_fields |  | No pagination | ✅ |  ❌  |
| form_entries | EntryId | DefaultPaginator | ✅ |  ❌  |
| reports | Hash | No pagination | ✅ |  ❌  |
| report_entries | EntryId | No pagination | ✅ |  ❌  |
| report_fields |  | No pagination | ✅ |  ❌  |
| report_widgets | Hash | No pagination | ✅ |  ❌  |
| users | Hash | No pagination | ✅ |  ❌  |

## Changelog

<details>
  <summary>Expand to review</summary>

| Version          | Date              | Pull Request | Subject        |
|------------------|-------------------|--------------|----------------|
| 0.0.1 | 2024-11-08 | | Initial release by [@parthiv11](https://github.com/parthiv11) via Connector Builder |

</details>

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
| 0.0.10 | 2025-02-01 | [53039](https://github.com/airbytehq/airbyte/pull/53039) | Update dependencies |
| 0.0.9 | 2025-01-25 | [52456](https://github.com/airbytehq/airbyte/pull/52456) | Update dependencies |
| 0.0.8 | 2025-01-18 | [52011](https://github.com/airbytehq/airbyte/pull/52011) | Update dependencies |
| 0.0.7 | 2025-01-11 | [51384](https://github.com/airbytehq/airbyte/pull/51384) | Update dependencies |
| 0.0.6 | 2024-12-28 | [50767](https://github.com/airbytehq/airbyte/pull/50767) | Update dependencies |
| 0.0.5 | 2024-12-21 | [50347](https://github.com/airbytehq/airbyte/pull/50347) | Update dependencies |
| 0.0.4 | 2024-12-14 | [49768](https://github.com/airbytehq/airbyte/pull/49768) | Update dependencies |
| 0.0.3 | 2024-12-12 | [49379](https://github.com/airbytehq/airbyte/pull/49379) | Update dependencies |
| 0.0.2 | 2024-12-11 | [49121](https://github.com/airbytehq/airbyte/pull/49121) | Starting with this version, the Docker image is now rootless. Please note that this and future versions will not be compatible with Airbyte versions earlier than 0.64 |
| 0.0.1 | 2024-11-08 | | Initial release by [@parthiv11](https://github.com/parthiv11) via Connector Builder |

</details>

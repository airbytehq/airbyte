# FeatureOS
FeatureOS : https://featureos.app/

## Configuration

| Input | Type | Description | Default Value |
|-------|------|-------------|---------------|
| `api_key` | `string` | API Key. Your FeatureOS API key. Generate it from FeatureOS organization settings. |  |
| `allow_private` | `boolean` | Allow Private Boards. Sets the ALLOW-PRIVATE header for post endpoints when syncing private board data. | false |
| `per_page` | `integer` | Page Size. Page size for endpoints that support per_page, such as posts and tags. | 30 |
| `bucket_id` | `` | Board ID. Optional board ID filter for feature_requests. |  |
| `approval_status` | `` | Approval Status. Optional post approval filter. |  |
| `submitter_emails` | `array` | Submitter Emails. Optional list of submitter emails to filter posts. | [] |
| `interactor_emails` | `array` | Interactor Emails. Optional list of interactor emails to filter posts. | [] |
| `tag_ids` | `array` | Tag IDs. Optional list of tag IDs to filter posts. | [] |
| `states` | `array` | Post States. Optional list of post status slugs to filter posts. | [] |
| `start_date` | `` | Start Date. Earliest record timestamp to sync incrementally. ISO-8601 recommended; defaults to 2020-01-01T00:00:00Z when omitted. |  |
| `sort` | `` | Post Sort. Optional sort mode for feature_requests. |  |
| `board_privacy` | `` | Board Privacy. Optional privacy filter for boards. |  |
| `board_sort` | `` | Board Sort. Optional alphabetical sort direction for boards. |  |
| `tag_source_type` | `` | Tag Source Type. Optional source type filter for tags. |  |
| `tag_source_id` | `` | Tag Source ID. Optional board ID when tag_source_type is bucket. |  |
| `tag_privacy` | `` | Tag Privacy. Optional privacy filter for tags. |  |

## Streams
| Stream Name | Primary Key | Pagination | Supports Full Sync | Supports Incremental |
|-------------|-------------|------------|---------------------|----------------------|
| organization_info |  | No pagination | ✅ |  ❌  |
| boards | id | No pagination | ✅ |  ❌  |
| tags | id | DefaultPaginator | ✅ |  ❌  |
| feature_requests | id | DefaultPaginator | ✅ |  ✅  |

## Changelog

<details>
  <summary>Expand to review</summary>

| Version          | Date              | Pull Request | Subject        |
|------------------|-------------------|--------------|----------------|
| 0.0.1 | 2026-03-26 | | Initial release by [@elibosley](https://github.com/elibosley) via Connector Builder |

</details>

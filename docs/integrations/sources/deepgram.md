# Deepgram
Syncs administrative data from the [Deepgram Management API](https://developers.deepgram.com/reference/manage): projects, API usage requests, API keys, balances, and usage summaries.

## Prerequisites

- A [Deepgram](https://deepgram.com/) account.
- A Deepgram API key with read scopes for the Management API (for example `project:read`, `usage:read`, `keys:read`, and `billing:read`). See [Authenticating](https://developers.deepgram.com/docs/authenticating) and [Create Additional API Keys](https://developers.deepgram.com/docs/create-additional-api-keys) in the Deepgram documentation.

## Configuration

| Input | Type | Description | Default Value |
|-------|------|-------------|---------------|
| `api_key` | `string` | API Key. Your Deepgram API key. Create one in the Deepgram Console under Settings &gt; API Keys. The key needs read scopes for the Management API (for example `project:read`, `usage:read`, `keys:read`, `billing:read`). |  |
| `start_date` | `string` | Start date. UTC date and time in the format 2020-01-01T00:00:00Z. Requests and usage created before this date will not be replicated. |  |

## Streams
| Stream Name | Primary Key | Pagination | Supports Full Sync | Supports Incremental |
|-------------|-------------|------------|---------------------|----------------------|
| projects | project_id | No pagination | ✅ |  ❌  |
| requests | request_id | DefaultPaginator | ✅ |  ✅  |
| keys | api_key_id | No pagination | ✅ |  ❌  |
| balances | balance_id | No pagination | ✅ |  ❌  |
| usage | project_id | No pagination | ✅ |  ❌  |
| usage_fields | project_id | No pagination | ✅ |  ❌  |

## Limitations & troubleshooting

- The `usage` and `usage_fields` streams return one summary record per project covering the range from `start_date` to today. All other streams are partitioned by project.
- The `requests` stream paginates with `page`/`limit` parameters (page size 1000) and syncs incrementally on the `created` field.

## IP allow list

If you use Airbyte Cloud and your organization restricts access to specific IPs, add the [Airbyte Cloud IP addresses](https://docs.airbyte.com/platform/operating-airbyte/ip-allowlist) to your allow list.

## Changelog

<details>
  <summary>Expand to review</summary>

| Version          | Date              | Pull Request | Subject        |
|------------------|-------------------|--------------|----------------|
| 0.1.0 | 2026-09-08 | [85757](https://github.com/airbytehq/airbyte/pull/85757) | Initial release of the Deepgram source connector |

</details>

# Zonka Feedback
This is the Zonka Feedback source that ingests data from the Zonka API.

Zonka Feedback simplifies CX, allowing you to start meaningful two-way conversations with customers via powerful surveys. Design stunning surveys in minutes, gather data from all touchpoints, understand customers better with AI analytics &amp; close the feedback loop — all within one powerful platform https://www.zonkafeedback.com/

To use this source, you must first create an account. Once logged in, click on Settings -&gt; Developers -&gt; API &amp; Data Center. Note down your Data center and generate your auth token. 

For more information about the API visit https://apidocs.zonkafeedback.com/#intro

## Configuration

| Input | Type | Description | Default Value |
|-------|------|-------------|---------------|
| `dc_id` | `string` | Data Center ID. The identifier for the data center, such as &#39;us1&#39; or &#39;e&#39; for EU. |  |
| `auth_token` | `string` | Auth Token. Auth token to use. Generate it by navigating to Company Settings &gt; Developers &gt; API in your Zonka Feedback account. |  |

## Streams
| Stream Name | Primary Key | Pagination | Supports Full Sync | Supports Incremental |
|-------------|-------------|------------|---------------------|----------------------|
| responses | id | DefaultPaginator | ✅ |  ❌  |
| workspaces | id | DefaultPaginator | ✅ |  ❌  |
| surveys | id | DefaultPaginator | ✅ |  ❌  |
| contacts | emailAddress | DefaultPaginator | ✅ |  ❌  |
| tasks | id | DefaultPaginator | ✅ |  ❌  |
| users | id | DefaultPaginator | ✅ |  ❌  |
| locations | id | DefaultPaginator | ✅ |  ❌  |

## Changelog

<details>
  <summary>Expand to review</summary>

| Version          | Date              | Pull Request | Subject        |
|------------------|-------------------|--------------|----------------|
| 0.0.22 | 2025-06-15 | [61230](https://github.com/airbytehq/airbyte/pull/61230) | Update dependencies |
| 0.0.21 | 2025-05-24 | [60747](https://github.com/airbytehq/airbyte/pull/60747) | Update dependencies |
| 0.0.20 | 2025-05-10 | [59986](https://github.com/airbytehq/airbyte/pull/59986) | Update dependencies |
| 0.0.19 | 2025-05-04 | [58941](https://github.com/airbytehq/airbyte/pull/58941) | Update dependencies |
| 0.0.18 | 2025-04-19 | [58571](https://github.com/airbytehq/airbyte/pull/58571) | Update dependencies |
| 0.0.17 | 2025-04-13 | [58048](https://github.com/airbytehq/airbyte/pull/58048) | Update dependencies |
| 0.0.16 | 2025-04-05 | [57374](https://github.com/airbytehq/airbyte/pull/57374) | Update dependencies |
| 0.0.15 | 2025-03-29 | [56834](https://github.com/airbytehq/airbyte/pull/56834) | Update dependencies |
| 0.0.14 | 2025-03-22 | [56344](https://github.com/airbytehq/airbyte/pull/56344) | Update dependencies |
| 0.0.13 | 2025-03-09 | [55656](https://github.com/airbytehq/airbyte/pull/55656) | Update dependencies |
| 0.0.12 | 2025-03-01 | [55159](https://github.com/airbytehq/airbyte/pull/55159) | Update dependencies |
| 0.0.11 | 2025-02-23 | [54633](https://github.com/airbytehq/airbyte/pull/54633) | Update dependencies |
| 0.0.10 | 2025-02-16 | [54125](https://github.com/airbytehq/airbyte/pull/54125) | Update dependencies |
| 0.0.9 | 2025-02-08 | [53597](https://github.com/airbytehq/airbyte/pull/53597) | Update dependencies |
| 0.0.8 | 2025-02-01 | [53123](https://github.com/airbytehq/airbyte/pull/53123) | Update dependencies |
| 0.0.7 | 2025-01-25 | [52550](https://github.com/airbytehq/airbyte/pull/52550) | Update dependencies |
| 0.0.6 | 2025-01-18 | [51939](https://github.com/airbytehq/airbyte/pull/51939) | Update dependencies |
| 0.0.5 | 2025-01-11 | [51471](https://github.com/airbytehq/airbyte/pull/51471) | Update dependencies |
| 0.0.4 | 2024-12-28 | [50829](https://github.com/airbytehq/airbyte/pull/50829) | Update dependencies |
| 0.0.3 | 2024-12-21 | [50388](https://github.com/airbytehq/airbyte/pull/50388) | Update dependencies |
| 0.0.2 | 2024-12-14 | [49454](https://github.com/airbytehq/airbyte/pull/49454) | Update dependencies |
| 0.0.1 | 2024-10-29 | | Initial release by [@aazam-gh](https://github.com/aazam-gh) via Connector Builder |

</details>

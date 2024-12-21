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
| 0.0.2 | 2024-12-14 | [49454](https://github.com/airbytehq/airbyte/pull/49454) | Update dependencies |
| 0.0.1 | 2024-10-29 | | Initial release by [@aazam-gh](https://github.com/aazam-gh) via Connector Builder |

</details>

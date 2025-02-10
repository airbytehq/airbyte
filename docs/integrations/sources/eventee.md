# Eventee
The Airbyte connector for Eventee enables seamless integration and automated data synchronization between Eventee, a leading event management platform, and your data destinations. It extracts and transfers event-related information such as attendee details, lectures, tracks, and more. This connector ensures real-time or scheduled data flow, helping you centralize and analyze Eventee&#39;s data effortlessly for improved event insights and reporting.

## Configuration

| Input | Type | Description | Default Value |
|-------|------|-------------|---------------|
| `api_token` | `string` | API Token. API token to use. Generate it at https://admin.eventee.co/ in &#39;Settings -&gt; Features&#39;. |  |

## Streams
| Stream Name | Primary Key | Pagination | Supports Full Sync | Supports Incremental |
|-------------|-------------|------------|---------------------|----------------------|
| halls | id | No pagination | ✅ |  ❌  |
| days | id | No pagination | ✅ |  ❌  |
| lectures | id | No pagination | ✅ |  ❌  |
| speakers | id | No pagination | ✅ |  ❌  |
| workshops | id | No pagination | ✅ |  ❌  |
| pauses | id | No pagination | ✅ |  ❌  |
| tracks | id | No pagination | ✅ |  ❌  |
| partners | id | No pagination | ✅ |  ❌  |
| participants | email | No pagination | ✅ |  ❌  |

## Changelog

<details>
  <summary>Expand to review</summary>

| Version          | Date              | Pull Request | Subject        |
|------------------|-------------------|--------------|----------------|
| 0.0.10 | 2025-02-08 | [53313](https://github.com/airbytehq/airbyte/pull/53313) | Update dependencies |
| 0.0.9 | 2025-02-01 | [52842](https://github.com/airbytehq/airbyte/pull/52842) | Update dependencies |
| 0.0.8 | 2025-01-25 | [52360](https://github.com/airbytehq/airbyte/pull/52360) | Update dependencies |
| 0.0.7 | 2025-01-18 | [51646](https://github.com/airbytehq/airbyte/pull/51646) | Update dependencies |
| 0.0.6 | 2025-01-11 | [51077](https://github.com/airbytehq/airbyte/pull/51077) | Update dependencies |
| 0.0.5 | 2024-12-28 | [50554](https://github.com/airbytehq/airbyte/pull/50554) | Update dependencies |
| 0.0.4 | 2024-12-21 | [50009](https://github.com/airbytehq/airbyte/pull/50009) | Update dependencies |
| 0.0.3 | 2024-12-14 | [49470](https://github.com/airbytehq/airbyte/pull/49470) | Update dependencies |
| 0.0.2 | 2024-12-12 | [49191](https://github.com/airbytehq/airbyte/pull/49191) | Update dependencies |
| 0.0.1 | 2024-10-28 | | Initial release by [@parthiv11](https://github.com/parthiv11) via Connector Builder |

</details>

# Bluetally
Connector for fetching asset and employee data from Bluetelly

## Configuration

| Input | Type | Description | Default Value |
|-------|------|-------------|---------------|
| `api_key` | `string` | API Key. Your API key to authenticate with the BlueTally API. You can generate it by navigating to your account settings, selecting &#39;API Keys&#39;, and clicking &#39;Create API Key&#39;. |  |
| `start_date` | `string` | Start date.  |  |

## Streams
| Stream Name | Primary Key | Pagination | Supports Full Sync | Supports Incremental |
|-------------|-------------|------------|---------------------|----------------------|
| assets | id | DefaultPaginator | ✅ |  ✅  |
| employees | id | DefaultPaginator | ✅ |  ✅  |

## Changelog

<details>
  <summary>Expand to review</summary>

| Version          | Date              | Pull Request | Subject        |
|------------------|-------------------|--------------|----------------|
| 0.0.18 | 2025-12-09 | [70645](https://github.com/airbytehq/airbyte/pull/70645) | Update dependencies |
| 0.0.17 | 2025-11-25 | [69980](https://github.com/airbytehq/airbyte/pull/69980) | Update dependencies |
| 0.0.16 | 2025-11-18 | [69429](https://github.com/airbytehq/airbyte/pull/69429) | Update dependencies |
| 0.0.15 | 2025-10-29 | [68735](https://github.com/airbytehq/airbyte/pull/68735) | Update dependencies |
| 0.0.14 | 2025-10-21 | [68214](https://github.com/airbytehq/airbyte/pull/68214) | Update dependencies |
| 0.0.13 | 2025-10-14 | [67814](https://github.com/airbytehq/airbyte/pull/67814) | Update dependencies |
| 0.0.12 | 2025-10-07 | [67202](https://github.com/airbytehq/airbyte/pull/67202) | Update dependencies |
| 0.0.11 | 2025-09-30 | [66324](https://github.com/airbytehq/airbyte/pull/66324) | Update dependencies |
| 0.0.10 | 2025-09-09 | [66033](https://github.com/airbytehq/airbyte/pull/66033) | Update dependencies |
| 0.0.9 | 2025-07-26 | [63790](https://github.com/airbytehq/airbyte/pull/63790) | Update dependencies |
| 0.0.8 | 2025-07-19 | [63456](https://github.com/airbytehq/airbyte/pull/63456) | Update dependencies |
| 0.0.7 | 2025-07-12 | [63065](https://github.com/airbytehq/airbyte/pull/63065) | Update dependencies |
| 0.0.6 | 2025-06-21 | [61090](https://github.com/airbytehq/airbyte/pull/61090) | Update dependencies |
| 0.0.5 | 2025-05-24 | [60732](https://github.com/airbytehq/airbyte/pull/60732) | Update dependencies |
| 0.0.4 | 2025-05-10 | [59337](https://github.com/airbytehq/airbyte/pull/59337) | Update dependencies |
| 0.0.3 | 2025-04-26 | [58714](https://github.com/airbytehq/airbyte/pull/58714) | Update dependencies |
| 0.0.2 | 2025-04-19 | [57644](https://github.com/airbytehq/airbyte/pull/57644) | Update dependencies |
| 0.0.1 | 2025-04-08 | | Initial release by [@wennergr](https://github.com/wennergr) via Connector Builder |

</details>

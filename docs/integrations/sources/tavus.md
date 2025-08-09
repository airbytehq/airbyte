# Tavus
Website: https://platform.tavus.io/
API Reference: https://docs.tavus.io/api-reference/phoenix-replica-model/get-replicas

## Configuration

| Input | Type | Description | Default Value |
|-------|------|-------------|---------------|
| `api_key` | `string` | API Key. Your Tavus API key. You can find this in your Tavus account settings or API dashboard. |  |
| `start_date` | `string` | Start date.  |  |

## Streams
| Stream Name | Primary Key | Pagination | Supports Full Sync | Supports Incremental |
|-------------|-------------|------------|---------------------|----------------------|
| replicas | replica_id | DefaultPaginator | ✅ |  ✅  |
| videos | video_id | DefaultPaginator | ✅ |  ❌  |
| conversations | conversation_id | DefaultPaginator | ✅ |  ✅  |
| personas | persona_id | DefaultPaginator | ✅ |  ✅  |
| speeches | speech_id | DefaultPaginator | ✅ |  ✅  |

## Changelog

<details>
  <summary>Expand to review</summary>

| Version          | Date              | Pull Request | Subject        |
|------------------|-------------------|--------------|----------------|
| 0.0.13 | 2025-08-09 | [64810](https://github.com/airbytehq/airbyte/pull/64810) | Update dependencies |
| 0.0.12 | 2025-07-26 | [63970](https://github.com/airbytehq/airbyte/pull/63970) | Update dependencies |
| 0.0.11 | 2025-07-19 | [63649](https://github.com/airbytehq/airbyte/pull/63649) | Update dependencies |
| 0.0.10 | 2025-07-12 | [63071](https://github.com/airbytehq/airbyte/pull/63071) | Update dependencies |
| 0.0.9 | 2025-07-05 | [62728](https://github.com/airbytehq/airbyte/pull/62728) | Update dependencies |
| 0.0.8 | 2025-06-28 | [62209](https://github.com/airbytehq/airbyte/pull/62209) | Update dependencies |
| 0.0.7 | 2025-06-14 | [60446](https://github.com/airbytehq/airbyte/pull/60446) | Update dependencies |
| 0.0.6 | 2025-05-10 | [60137](https://github.com/airbytehq/airbyte/pull/60137) | Update dependencies |
| 0.0.5 | 2025-05-04 | [59607](https://github.com/airbytehq/airbyte/pull/59607) | Update dependencies |
| 0.0.4 | 2025-04-27 | [59000](https://github.com/airbytehq/airbyte/pull/59000) | Update dependencies |
| 0.0.3 | 2025-04-19 | [58383](https://github.com/airbytehq/airbyte/pull/58383) | Update dependencies |
| 0.0.2 | 2025-04-12 | [57929](https://github.com/airbytehq/airbyte/pull/57929) | Update dependencies |
| 0.0.1 | 2025-04-05 | [#57022](https://github.com/airbytehq/airbyte/pull/57022) | Initial release by [@btkcodedev](https://github.com/btkcodedev) via Connector Builder |

</details>

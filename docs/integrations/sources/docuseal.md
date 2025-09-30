# Docuseal
Website: https://docuseal.com/
API Reference: https://www.docuseal.com/docs/api

## Configuration

| Input | Type | Description | Default Value |
|-------|------|-------------|---------------|
| `api_key` | `string` | API Key. Your API key for authenticating with the DocuSeal API. Obtain it from the DocuSeal API Console at https://console.docuseal.com/api. |  |
| `start_date` | `string` | Start date.  |  |
| `limit` | `string` | Limit. The pagination limit | 5 |

## Streams
| Stream Name | Primary Key | Pagination | Supports Full Sync | Supports Incremental |
|-------------|-------------|------------|---------------------|----------------------|
| submissions | id | DefaultPaginator | ✅ |  ✅  |
| templates | id | DefaultPaginator | ✅ |  ✅  |
| submitters | id | DefaultPaginator | ✅ |  ✅  |

## Changelog

<details>
  <summary>Expand to review</summary>

| Version          | Date              | Pull Request | Subject        |
|------------------|-------------------|--------------|----------------|
| 0.0.18 | 2025-08-23 | [65306](https://github.com/airbytehq/airbyte/pull/65306) | Update dependencies |
| 0.0.17 | 2025-08-09 | [64668](https://github.com/airbytehq/airbyte/pull/64668) | Update dependencies |
| 0.0.16 | 2025-08-02 | [64322](https://github.com/airbytehq/airbyte/pull/64322) | Update dependencies |
| 0.0.15 | 2025-07-26 | [63960](https://github.com/airbytehq/airbyte/pull/63960) | Update dependencies |
| 0.0.14 | 2025-07-19 | [63582](https://github.com/airbytehq/airbyte/pull/63582) | Update dependencies |
| 0.0.13 | 2025-07-12 | [63028](https://github.com/airbytehq/airbyte/pull/63028) | Update dependencies |
| 0.0.12 | 2025-07-05 | [62803](https://github.com/airbytehq/airbyte/pull/62803) | Update dependencies |
| 0.0.11 | 2025-06-28 | [62426](https://github.com/airbytehq/airbyte/pull/62426) | Update dependencies |
| 0.0.10 | 2025-06-21 | [61957](https://github.com/airbytehq/airbyte/pull/61957) | Update dependencies |
| 0.0.9 | 2025-06-14 | [61280](https://github.com/airbytehq/airbyte/pull/61280) | Update dependencies |
| 0.0.8 | 2025-05-24 | [60369](https://github.com/airbytehq/airbyte/pull/60369) | Update dependencies |
| 0.0.7 | 2025-05-10 | [60031](https://github.com/airbytehq/airbyte/pull/60031) | Update dependencies |
| 0.0.6 | 2025-05-03 | [59426](https://github.com/airbytehq/airbyte/pull/59426) | Update dependencies |
| 0.0.5 | 2025-04-26 | [58904](https://github.com/airbytehq/airbyte/pull/58904) | Update dependencies |
| 0.0.4 | 2025-04-19 | [58316](https://github.com/airbytehq/airbyte/pull/58316) | Update dependencies |
| 0.0.3 | 2025-04-12 | [57831](https://github.com/airbytehq/airbyte/pull/57831) | Update dependencies |
| 0.0.2 | 2025-04-05 | [57272](https://github.com/airbytehq/airbyte/pull/57272) | Update dependencies |
| 0.0.1 | 2025-04-01 | | Initial release by [@btkcodedev](https://github.com/btkcodedev) via Connector Builder |

</details>

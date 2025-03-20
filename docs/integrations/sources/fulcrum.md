# Fulcrum
Airbyte connector for Fulcrum would enable seamless data extraction from the Fulcrum platform, allowing users to sync survey and field data with their data warehouses or other applications. This connector would facilitate automated, scheduled transfers of structured data, improving analytics, reporting, and decision-making processes by integrating Fulcrum's powerful field data collection capabilities with a broader data ecosystem.

## Configuration

| Input | Type | Description | Default Value |
|-------|------|-------------|---------------|
| `api_key` | `string` | API Key. API key to use. Find it at https://web.fulcrumapp.com/settings/api |  |

## Streams
| Stream Name | Primary Key | Pagination | Supports Full Sync | Supports Incremental |
|-------------|-------------|------------|---------------------|----------------------|
| forms | id | DefaultPaginator | ✅ |  ❌  |
| users | id | DefaultPaginator | ✅ |  ❌  |
| workflows |  | DefaultPaginator | ✅ |  ❌  |
| webhooks | id | DefaultPaginator | ✅ |  ❌  |
| changesets | id | DefaultPaginator | ✅ |  ❌  |
| records | id | DefaultPaginator | ✅ |  ❌  |
| signatures | record_id | DefaultPaginator | ✅ |  ❌  |
| projects | id | DefaultPaginator | ✅ |  ❌  |
| layers | id | DefaultPaginator | ✅ |  ❌  |
| classification_sets | id | DefaultPaginator | ✅ |  ❌  |
| choice_lists | id | DefaultPaginator | ✅ |  ❌  |
| groups | id | DefaultPaginator | ✅ |  ❌  |
| memberships | id | DefaultPaginator | ✅ |  ❌  |
| roles | id | DefaultPaginator | ✅ |  ❌  |
| authorizations | id | DefaultPaginator | ✅ |  ❌  |
| photos | record_id | DefaultPaginator | ✅ |  ❌  |
| audio | record_id | DefaultPaginator | ✅ |  ❌  |
| videos | record_id | DefaultPaginator | ✅ |  ❌  |

## Changelog

<details>
  <summary>Expand to review</summary>

| Version          | Date              | Pull Request | Subject        |
|------------------|-------------------|--------------|----------------|
| 0.0.15 | 2025-03-08 | [55312](https://github.com/airbytehq/airbyte/pull/55312) | Update dependencies |
| 0.0.14 | 2025-03-01 | [54409](https://github.com/airbytehq/airbyte/pull/54409) | Update dependencies |
| 0.0.13 | 2025-02-15 | [53769](https://github.com/airbytehq/airbyte/pull/53769) | Update dependencies |
| 0.0.12 | 2025-02-08 | [53319](https://github.com/airbytehq/airbyte/pull/53319) | Update dependencies |
| 0.0.11 | 2025-02-01 | [52839](https://github.com/airbytehq/airbyte/pull/52839) | Update dependencies |
| 0.0.10 | 2025-01-25 | [52324](https://github.com/airbytehq/airbyte/pull/52324) | Update dependencies |
| 0.0.9 | 2025-01-18 | [51627](https://github.com/airbytehq/airbyte/pull/51627) | Update dependencies |
| 0.0.8 | 2025-01-11 | [51138](https://github.com/airbytehq/airbyte/pull/51138) | Update dependencies |
| 0.0.7 | 2024-12-28 | [50560](https://github.com/airbytehq/airbyte/pull/50560) | Update dependencies |
| 0.0.6 | 2024-12-21 | [50038](https://github.com/airbytehq/airbyte/pull/50038) | Update dependencies |
| 0.0.5 | 2024-12-14 | [49512](https://github.com/airbytehq/airbyte/pull/49512) | Update dependencies |
| 0.0.4 | 2024-12-12 | [49200](https://github.com/airbytehq/airbyte/pull/49200) | Update dependencies |
| 0.0.3 | 2024-11-05 | [48358](https://github.com/airbytehq/airbyte/pull/48358) | Revert to source-declarative-manifest v5.17.0 |
| 0.0.2 | 2024-11-05 | [48333](https://github.com/airbytehq/airbyte/pull/48333) | Update dependencies |
| 0.0.1 | 2024-10-21 | | Initial release by [@parthiv11](https://github.com/parthiv11) via Connector Builder |

</details>

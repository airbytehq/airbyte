# Pipeliner

Pipeliner is a CRM tool.
Using this connector we fetch data from various streams such as contacts, data, leads and quotes.
[API Docs](https://pipeliner.stoplight.io/docs/api-docs)

## Configuration

| Input | Type | Description | Default Value |
|-------|------|-------------|---------------|
| `username` | `string` | Username.  |  |
| `password` | `string` | Password.  |  |
| `service` | `string` | Data Center.  |  |
| `spaceid` | `string` | Space ID.  |  |

## Streams
| Stream Name | Primary Key | Pagination | Supports Full Sync | Supports Incremental |
|-------------|-------------|------------|---------------------|----------------------|
| accounts | id | DefaultPaginator | ✅ |  ❌  |
| activities | id | DefaultPaginator | ✅ |  ❌  |
| clients | id | DefaultPaginator | ✅ |  ❌  |
| contacts | id | DefaultPaginator | ✅ |  ❌  |
| entities | id | DefaultPaginator | ✅ |  ❌  |
| data | id | DefaultPaginator | ✅ |  ❌  |
| cloud_objects | id | DefaultPaginator | ✅ |  ❌  |
| fields | id | DefaultPaginator | ✅ |  ❌  |
| forecasts | id | DefaultPaginator | ✅ |  ❌  |
| form_views | id | DefaultPaginator | ✅ |  ❌  |
| entity_scorings | id | DefaultPaginator | ✅ |  ❌  |
| leads | id | DefaultPaginator | ✅ |  ❌  |
| lead_oppties | id | DefaultPaginator | ✅ |  ❌  |
| memos | id | DefaultPaginator | ✅ |  ❌  |
| notes | id | DefaultPaginator | ✅ |  ❌  |
| entity_fitnesses | id | DefaultPaginator | ✅ |  ❌  |
| pipelines | id | DefaultPaginator | ✅ |  ❌  |
| products | id | DefaultPaginator | ✅ |  ❌  |
| oppty_product_relations | id | DefaultPaginator | ✅ |  ❌  |
| profiles | id | DefaultPaginator | ✅ |  ❌  |
| quotes | id | DefaultPaginator | ✅ |  ❌  |
| reports | id | DefaultPaginator | ✅ |  ❌  |
| steps | id | DefaultPaginator | ✅ |  ❌  |
| tags | id | DefaultPaginator | ✅ |  ❌  |

## Changelog

<details>
  <summary>Expand to review</summary>

| Version          | Date              | Pull Request | Subject        |
|------------------|-------------------|--------------|----------------|
| 0.0.9 | 2025-01-25 | [52512](https://github.com/airbytehq/airbyte/pull/52512) | Update dependencies |
| 0.0.8 | 2025-01-18 | [51877](https://github.com/airbytehq/airbyte/pull/51877) | Update dependencies |
| 0.0.7 | 2025-01-11 | [51358](https://github.com/airbytehq/airbyte/pull/51358) | Update dependencies |
| 0.0.6 | 2024-12-28 | [50694](https://github.com/airbytehq/airbyte/pull/50694) | Update dependencies |
| 0.0.5 | 2024-12-21 | [50276](https://github.com/airbytehq/airbyte/pull/50276) | Update dependencies |
| 0.0.4 | 2024-12-14 | [49656](https://github.com/airbytehq/airbyte/pull/49656) | Update dependencies |
| 0.0.3 | 2024-12-12 | [49321](https://github.com/airbytehq/airbyte/pull/49321) | Update dependencies |
| 0.0.2 | 2024-12-11 | [49077](https://github.com/airbytehq/airbyte/pull/49077) | Starting with this version, the Docker image is now rootless. Please note that this and future versions will not be compatible with Airbyte versions earlier than 0.64 |
| 0.0.1 | 2024-11-09 | | Initial release by [@ombhardwajj](https://github.com/ombhardwajj) via Connector Builder |

</details>

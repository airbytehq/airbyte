# Pipeliner
Pipeliner is a CRM tool.
Using this connector we fetch data from various streams such as contacts , data , leads and quotes.
Docs : https://pipeliner.stoplight.io/docs/api-docs

## Configuration

| Input | Type | Description | Default Value |
|-------|------|-------------|---------------|
| `username` | `string` | Username.  |  |
| `password` | `string` | Password.  |  |
| `service` | `string` | Service.  |  |
| `spaceid` | `string` | SpaceID.  |  |

## Streams
| Stream Name | Primary Key | Pagination | Supports Full Sync | Supports Incremental |
|-------------|-------------|------------|---------------------|----------------------|
| accounts | id | No pagination | ✅ |  ❌  |
| activities | id | No pagination | ✅ |  ❌  |
| clients | id | No pagination | ✅ |  ❌  |
| contacts | id | No pagination | ✅ |  ❌  |
| entities | id | No pagination | ✅ |  ❌  |
| data | id | No pagination | ✅ |  ❌  |
| cloud_objects | id | No pagination | ✅ |  ❌  |
| fields | id | No pagination | ✅ |  ❌  |
| forecasts | id | No pagination | ✅ |  ❌  |
| form_views | id | No pagination | ✅ |  ❌  |
| entity_scorings | id | No pagination | ✅ |  ❌  |
| leads | id | No pagination | ✅ |  ❌  |
| lead_oppties | id | No pagination | ✅ |  ❌  |
| memos | id | No pagination | ✅ |  ❌  |
| notes | id | No pagination | ✅ |  ❌  |
| entity_fitnesses | id | No pagination | ✅ |  ❌  |
| pipelines | id | No pagination | ✅ |  ❌  |
| products | id | No pagination | ✅ |  ❌  |
| oppty_product_relations | id | No pagination | ✅ |  ❌  |
| profiles | id | No pagination | ✅ |  ❌  |
| quotes | id | No pagination | ✅ |  ❌  |
| reports | id | No pagination | ✅ |  ❌  |
| steps | id | No pagination | ✅ |  ❌  |
| tags | id | No pagination | ✅ |  ❌  |

## Changelog

<details>
  <summary>Expand to review</summary>

| Version          | Date              | Pull Request | Subject        |
|------------------|-------------------|--------------|----------------|
| 0.0.1 | 2024-10-31 | | Initial release by [@ombhardwajj](https://github.com/ombhardwajj) via Connector Builder |

</details>

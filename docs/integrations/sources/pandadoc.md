# PandaDoc
Airbyte connector for PandaDoc allows users to extract data from PandaDoc and integrate it into various data warehouses or databases. This connector functions as a source, pulling data such as documents, templates, and related metadata from PandaDoc.

## Configuration

| Input | Type | Description | Default Value |
|-------|------|-------------|---------------|
| `api_key` | `string` | API Key. API key to use. Find it at https://app.pandadoc.com/a/#/settings/api-dashboard/configuration |  |
| `start_date` | `string` | Start date.  |  |

## Streams
| Stream Name | Primary Key | Pagination | Supports Full Sync | Supports Incremental |
|-------------|-------------|------------|---------------------|----------------------|
| documents | id | DefaultPaginator | ✅ |  ✅  |
| document_attachment | uuid | No pagination | ✅ |  ❌  |
| document_field | uuid | No pagination | ✅ |  ❌  |
| document_section | uuid | No pagination | ✅ |  ❌  |
| templates |  | DefaultPaginator | ✅ |  ❌  |
| forms | id | No pagination | ✅ |  ✅  |
| contacts | id | No pagination | ✅ |  ❌  |
| members | user_id | No pagination | ✅ |  ✅  |
| api_logs | id | DefaultPaginator | ✅ |  ❌  |
| document_folders | uuid | DefaultPaginator | ✅ |  ❌  |
| template_folders | uuid | No pagination | ✅ |  ❌  |
| workspaces | id | DefaultPaginator | ✅ |  ❌  |
| webhook_subscriptions | uuid | No pagination | ✅ |  ❌  |
| webhook_events | uuid | DefaultPaginator | ✅ |  ❌  |

## Changelog

<details>
  <summary>Expand to review</summary>

| Version          | Date              | Pull Request | Subject        |
|------------------|-------------------|--------------|----------------|
| 0.0.45 | 2025-12-09 | [70483](https://github.com/airbytehq/airbyte/pull/70483) | Update dependencies |
| 0.0.44 | 2025-11-25 | [70084](https://github.com/airbytehq/airbyte/pull/70084) | Update dependencies |
| 0.0.43 | 2025-11-18 | [69710](https://github.com/airbytehq/airbyte/pull/69710) | Update dependencies |
| 0.0.42 | 2025-10-29 | [68996](https://github.com/airbytehq/airbyte/pull/68996) | Update dependencies |
| 0.0.41 | 2025-10-21 | [68309](https://github.com/airbytehq/airbyte/pull/68309) | Update dependencies |
| 0.0.40 | 2025-10-14 | [67803](https://github.com/airbytehq/airbyte/pull/67803) | Update dependencies |
| 0.0.39 | 2025-10-07 | [67337](https://github.com/airbytehq/airbyte/pull/67337) | Update dependencies |
| 0.0.38 | 2025-09-30 | [66391](https://github.com/airbytehq/airbyte/pull/66391) | Update dependencies |
| 0.0.37 | 2025-09-09 | [65787](https://github.com/airbytehq/airbyte/pull/65787) | Update dependencies |
| 0.0.36 | 2025-08-23 | [65225](https://github.com/airbytehq/airbyte/pull/65225) | Update dependencies |
| 0.0.35 | 2025-08-09 | [64704](https://github.com/airbytehq/airbyte/pull/64704) | Update dependencies |
| 0.0.34 | 2025-08-02 | [64236](https://github.com/airbytehq/airbyte/pull/64236) | Update dependencies |
| 0.0.33 | 2025-07-26 | [63844](https://github.com/airbytehq/airbyte/pull/63844) | Update dependencies |
| 0.0.32 | 2025-07-19 | [63395](https://github.com/airbytehq/airbyte/pull/63395) | Update dependencies |
| 0.0.31 | 2025-07-12 | [63232](https://github.com/airbytehq/airbyte/pull/63232) | Update dependencies |
| 0.0.30 | 2025-07-05 | [62635](https://github.com/airbytehq/airbyte/pull/62635) | Update dependencies |
| 0.0.29 | 2025-06-28 | [62411](https://github.com/airbytehq/airbyte/pull/62411) | Update dependencies |
| 0.0.28 | 2025-06-21 | [61926](https://github.com/airbytehq/airbyte/pull/61926) | Update dependencies |
| 0.0.27 | 2025-06-14 | [61023](https://github.com/airbytehq/airbyte/pull/61023) | Update dependencies |
| 0.0.26 | 2025-05-24 | [60469](https://github.com/airbytehq/airbyte/pull/60469) | Update dependencies |
| 0.0.25 | 2025-05-10 | [60175](https://github.com/airbytehq/airbyte/pull/60175) | Update dependencies |
| 0.0.24 | 2025-05-03 | [59462](https://github.com/airbytehq/airbyte/pull/59462) | Update dependencies |
| 0.0.23 | 2025-04-27 | [59058](https://github.com/airbytehq/airbyte/pull/59058) | Update dependencies |
| 0.0.22 | 2025-04-19 | [58462](https://github.com/airbytehq/airbyte/pull/58462) | Update dependencies |
| 0.0.21 | 2025-04-12 | [57859](https://github.com/airbytehq/airbyte/pull/57859) | Update dependencies |
| 0.0.20 | 2025-04-05 | [57362](https://github.com/airbytehq/airbyte/pull/57362) | Update dependencies |
| 0.0.19 | 2025-03-29 | [56767](https://github.com/airbytehq/airbyte/pull/56767) | Update dependencies |
| 0.0.18 | 2025-03-22 | [56220](https://github.com/airbytehq/airbyte/pull/56220) | Update dependencies |
| 0.0.17 | 2025-03-08 | [55560](https://github.com/airbytehq/airbyte/pull/55560) | Update dependencies |
| 0.0.16 | 2025-03-01 | [55029](https://github.com/airbytehq/airbyte/pull/55029) | Update dependencies |
| 0.0.15 | 2025-02-23 | [54579](https://github.com/airbytehq/airbyte/pull/54579) | Update dependencies |
| 0.0.14 | 2025-02-15 | [53955](https://github.com/airbytehq/airbyte/pull/53955) | Update dependencies |
| 0.0.13 | 2025-02-08 | [53471](https://github.com/airbytehq/airbyte/pull/53471) | Update dependencies |
| 0.0.12 | 2025-02-01 | [52975](https://github.com/airbytehq/airbyte/pull/52975) | Update dependencies |
| 0.0.11 | 2025-01-25 | [52482](https://github.com/airbytehq/airbyte/pull/52482) | Update dependencies |
| 0.0.10 | 2025-01-18 | [51890](https://github.com/airbytehq/airbyte/pull/51890) | Update dependencies |
| 0.0.9 | 2025-01-11 | [51373](https://github.com/airbytehq/airbyte/pull/51373) | Update dependencies |
| 0.0.8 | 2024-12-28 | [50681](https://github.com/airbytehq/airbyte/pull/50681) | Update dependencies |
| 0.0.7 | 2024-12-21 | [50268](https://github.com/airbytehq/airbyte/pull/50268) | Update dependencies |
| 0.0.6 | 2024-12-14 | [49702](https://github.com/airbytehq/airbyte/pull/49702) | Update dependencies |
| 0.0.5 | 2024-12-12 | [49354](https://github.com/airbytehq/airbyte/pull/49354) | Update dependencies |
| 0.0.4 | 2024-12-11 | [49064](https://github.com/airbytehq/airbyte/pull/49064) | Starting with this version, the Docker image is now rootless. Please note that this and future versions will not be compatible with Airbyte versions earlier than 0.64 |
| 0.0.3 | 2024-11-04 | [48210](https://github.com/airbytehq/airbyte/pull/48210) | Update dependencies |
| 0.0.2 | 2024-10-29 | [47911](https://github.com/airbytehq/airbyte/pull/47911) | Update dependencies |
| 0.0.1 | 2024-10-21 | | Initial release by [@parthiv11](https://github.com/parthiv11) via Connector Builder |

</details>

# Rocketlane
Rocketlane connector  enables seamless data integration by syncing project, task, and user data from Rocketlane into various data warehouses or analytics platforms. It ensures real-time access to operational insights, enhancing project visibility and performance tracking across tools.

## Configuration

| Input | Type | Description | Default Value |
|-------|------|-------------|---------------|
| `api_key` | `string` | API Key. API key to use. Generate it from the API section in Settings of your Rocketlane account. |  |

## Streams
| Stream Name | Primary Key | Pagination | Supports Full Sync | Supports Incremental |
|-------------|-------------|------------|---------------------|----------------------|
| tasks | taskId | DefaultPaginator | ✅ |  ❌  |
| users | userId | DefaultPaginator | ✅ |  ❌  |
| projects | projectId | DefaultPaginator | ✅ |  ❌  |
| fields | fieldId | DefaultPaginator | ✅ |  ❌  |
| time-offs | timeOffId | DefaultPaginator | ✅ |  ❌  |
| spaces | spaceId | DefaultPaginator | ✅ |  ❌  |
| phases | phaseId | DefaultPaginator | ✅ |  ❌  |
| time-entries | timeEntryId | DefaultPaginator | ✅ |  ❌  |
| space-documents | spaceDocumentId | DefaultPaginator | ✅ |  ❌  |

## Changelog

<details>
  <summary>Expand to review</summary>

| Version          | Date              | Pull Request | Subject        |
|------------------|-------------------|--------------|----------------|
| 0.0.21 | 2025-05-11 | [60210](https://github.com/airbytehq/airbyte/pull/60210) | Update dependencies |
| 0.0.20 | 2025-05-04 | [59587](https://github.com/airbytehq/airbyte/pull/59587) | Update dependencies |
| 0.0.19 | 2025-04-27 | [59017](https://github.com/airbytehq/airbyte/pull/59017) | Update dependencies |
| 0.0.18 | 2025-04-19 | [58445](https://github.com/airbytehq/airbyte/pull/58445) | Update dependencies |
| 0.0.17 | 2025-04-12 | [58009](https://github.com/airbytehq/airbyte/pull/58009) | Update dependencies |
| 0.0.16 | 2025-04-05 | [57344](https://github.com/airbytehq/airbyte/pull/57344) | Update dependencies |
| 0.0.15 | 2025-03-29 | [56763](https://github.com/airbytehq/airbyte/pull/56763) | Update dependencies |
| 0.0.14 | 2025-03-22 | [56192](https://github.com/airbytehq/airbyte/pull/56192) | Update dependencies |
| 0.0.13 | 2025-03-08 | [55059](https://github.com/airbytehq/airbyte/pull/55059) | Update dependencies |
| 0.0.12 | 2025-02-23 | [54599](https://github.com/airbytehq/airbyte/pull/54599) | Update dependencies |
| 0.0.11 | 2025-02-15 | [53980](https://github.com/airbytehq/airbyte/pull/53980) | Update dependencies |
| 0.0.10 | 2025-02-08 | [53470](https://github.com/airbytehq/airbyte/pull/53470) | Update dependencies |
| 0.0.9 | 2025-02-01 | [52964](https://github.com/airbytehq/airbyte/pull/52964) | Update dependencies |
| 0.0.8 | 2025-01-25 | [52506](https://github.com/airbytehq/airbyte/pull/52506) | Update dependencies |
| 0.0.7 | 2025-01-18 | [51908](https://github.com/airbytehq/airbyte/pull/51908) | Update dependencies |
| 0.0.6 | 2025-01-11 | [51330](https://github.com/airbytehq/airbyte/pull/51330) | Update dependencies |
| 0.0.5 | 2024-12-28 | [50688](https://github.com/airbytehq/airbyte/pull/50688) | Update dependencies |
| 0.0.4 | 2024-12-21 | [50227](https://github.com/airbytehq/airbyte/pull/50227) | Update dependencies |
| 0.0.3 | 2024-12-14 | [49673](https://github.com/airbytehq/airbyte/pull/49673) | Update dependencies |
| 0.0.2 | 2024-12-12 | [49068](https://github.com/airbytehq/airbyte/pull/49068) | Update dependencies |
| 0.0.1 | 2024-11-08 | | Initial release by [@bishalbera](https://github.com/bishalbera) via Connector Builder |

</details>

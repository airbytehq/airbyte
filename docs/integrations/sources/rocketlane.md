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

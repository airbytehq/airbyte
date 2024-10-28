# Attio
The Attio Airbyte Connector enables seamless integration with Attio, a modern CRM platform. This connector allows you to easily extract, sync, and manage data from Attio, such as contacts, accounts, and interactions, directly into your preferred data destinations. With this integration, businesses can streamline workflows, perform advanced analytics, and create automated pipelines for their CRM data, ensuring data consistency and accessibility across tools.

## Configuration

| Input | Type | Description | Default Value |
|-------|------|-------------|---------------|
| `bearer_token` | `string` | Bearer Token. Permanent Bearer Token for accessing the Attio API. Obtain it from your Attio account settings or API management page. |  |

## Streams
| Stream Name | Primary Key | Pagination | Supports Full Sync | Supports Incremental |
|-------------|-------------|------------|---------------------|----------------------|
| objects | object_id | No pagination | ✅ |  ❌  |
| object_attributes |  | DefaultPaginator | ✅ |  ❌  |
| records | record_id | No pagination | ✅ |  ❌  |
| lists | list_id | No pagination | ✅ |  ❌  |
| meta | workspace_id | No pagination | ✅ |  ❌  |
| entries |  | DefaultPaginator | ✅ |  ❌  |
| workspace_members | workspace_member_id | No pagination | ✅ |  ❌  |
| notes | note_id | DefaultPaginator | ✅ |  ❌  |
| tasks | task_id | DefaultPaginator | ✅ |  ❌  |
| webhooks |  | DefaultPaginator | ✅ |  ❌  |

## Changelog

<details>
  <summary>Expand to review</summary>

| Version          | Date              | Pull Request | Subject        |
|------------------|-------------------|--------------|----------------|
| 0.0.1 | 2024-10-28 | | Initial release by [@parthiv11](https://github.com/parthiv11) via Connector Builder |

</details>

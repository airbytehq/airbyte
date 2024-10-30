# Firehydrant
This is the Firehydrant source that ingests data from the Firehydrant API.

FireHydrant is with you throughout the entire incident lifecycle from first alert until you&#39;ve learned from the retrospective. Reduce alert fatigue, guide responders, reduce MTTR and run stress-less retrospectives - all in a single, unified platform https://firehydrant.com

To use this source you must first create an account. Once logged in, head over to settings and in the sidebar, under Integrations click on API Keys. Click on Create a New API Key and note it down. 
You can find more information about the API here https://developers.firehydrant.com/#/

## Configuration

| Input | Type | Description | Default Value |
|-------|------|-------------|---------------|
| `api_token` | `string` | API Token. Bot token to authenticate with the FireHydrant API. You can find it by logging into your organization and navigating to the Bot users page at https://app.firehydrant.io/organizations/bots. |  |

## Streams
| Stream Name | Primary Key | Pagination | Supports Full Sync | Supports Incremental |
|-------------|-------------|------------|---------------------|----------------------|
| environments | id | DefaultPaginator | ✅ |  ❌  |
| services | id | DefaultPaginator | ✅ |  ❌  |
| functionalities | id | DefaultPaginator | ✅ |  ❌  |
| teams | id | DefaultPaginator | ✅ |  ❌  |
| incidents | id | DefaultPaginator | ✅ |  ❌  |
| users | id | DefaultPaginator | ✅ |  ❌  |
| task_lists | id | DefaultPaginator | ✅ |  ❌  |
| runbook_actions | id | DefaultPaginator | ✅ |  ❌  |
| priorities | slug | DefaultPaginator | ✅ |  ❌  |
| severities | slug | DefaultPaginator | ✅ |  ❌  |
| scheduled_maintenences | id | DefaultPaginator | ✅ |  ❌  |
| alerts | id | DefaultPaginator | ✅ |  ❌  |
| tickets | id | DefaultPaginator | ✅ |  ❌  |
| schedules | id | DefaultPaginator | ✅ |  ❌  |

## Changelog

<details>
  <summary>Expand to review</summary>

| Version          | Date              | Pull Request | Subject        |
|------------------|-------------------|--------------|----------------|
| 0.0.1 | 2024-10-30 | | Initial release by [@aazam-gh](https://github.com/aazam-gh) via Connector Builder |

</details>

# SafetyCulture

This is the guide for the Safetyculture source connector which ingests data from the Safetyculture API.

## Prerequisites

This source uses the Authorization Bearer Token for handling requests. In order to obtain the credientials, you must first create a Safetyculture account.
The API usage is only availabe for paid plans https://www.safetyculture.com/

Once you have created your account, you can log in to your account.
You can create an API token under Account Settings -> Integrations -> Manage MY API Tokens
You can find more about their API here https://developer.safetyculture.com/reference/introduction

## Set up the Adjust source connector

1. Click **Sources** and then click **+ New source**.
2. On the Set up the source page, select **Safetyculture** from the Source type dropdown.
3. Enter a name for your new source.
4. For **API Token**, enter your API token obtained in the previous step.
5. Click **Set up source**.

## Supported sync modes

The source connector supports the following [sync modes](https://docs.airbyte.com/cloud/core-concepts#connection-sync-modes):

- Full Refresh

## Configuration

| Input | Type | Description | Default Value |
|-------|------|-------------|---------------|
| `api_key` | `string` | API Key.  |  |

## Streams
| Stream Name | Primary Key | Pagination | Supports Full Sync | Supports Incremental |
|-------------|-------------|------------|---------------------|----------------------|
| feed_users | id | DefaultPaginator | ✅ |  ❌  |
| groups | id | No pagination | ✅ |  ❌  |
| connections | id | No pagination | ✅ |  ❌  |
| heads_up | id | DefaultPaginator | ✅ |  ❌  |
| assets | id | DefaultPaginator | ✅ |  ❌  |
| folders | id | DefaultPaginator | ✅ |  ❌  |
| global_response_sets | responseset_id | No pagination | ✅ |  ❌  |
| schedule_items | id | DefaultPaginator | ✅ |  ❌  |
| actions | unique_id | DefaultPaginator | ✅ |  ❌  |
| templates | template_id | No pagination | ✅ |  ❌  |
| feed_templates | id | DefaultPaginator | ✅ |  ❌  |
| issues | unique_id | DefaultPaginator | ✅ |  ❌  |

## Changelog

<details>
  <summary>Expand to review</summary>

| Version          | Date              | Pull Request | Subject        |
|------------------|-------------------|--------------|----------------|
| 0.0.1 | 2024-10-04 | | Initial release by [@aazam-gh](https://github.com/aazam-gh) via Connector Builder |

</details>

# Campaign Monitor

This is the setup for the Campaign Monitor source which ingests data from the campaign monitor api.
The different types of `campaign` endpoints are available in this source.

## Prerequisites

A username and password associated with your Campaign Monitor account is required for authentication.
You can get your API key from the Account Settings page when logged into your Campaign Monitor account. 
Enter the API key in the username field and enter any value in the password field https://www.campaignmonitor.com/api/v3-3/getting-started/ 

You can specify a `start_date` for replicating data from the beginning of that date.

## Set up the Adjust source connector

1. Click **Sources** and then click **+ New source**.
2. On the Set up the source page, select **Campaign Monitor** from the Source type dropdown.
3. Enter a name for your new source.
4. For **username**, enter your API key obtained in the previous step.
5. For **password**, enter your any dummy value.
6. For **start_date**, enter a date in YYYY-MM-DD format (UTC timezone is assumed). Data starting from this date will be replicated.
8. Click **Set up source**.

## Supported sync modes

The source connector supports the following [sync modes](https://docs.airbyte.com/cloud/core-concepts#connection-sync-modes):

- Full Refresh
- Incremental

## Configuration

| Input | Type | Description | Default Value |
|-------|------|-------------|---------------|
| `username` | `string` | Username.  |  |
| `password` | `string` | Password.  |  |
| `start_date` | `string` | start_date. Date from when the sync should start |  |

## Streams
| Stream Name | Primary Key | Pagination | Supports Full Sync | Supports Incremental |
|-------------|-------------|------------|---------------------|----------------------|
| clients | ClientID | No pagination | ✅ |  ❌  |
| admins | EmailAddress | No pagination | ✅ |  ❌  |
| client_details | ClientID | No pagination | ✅ |  ❌  |
| segments | SegmentID | No pagination | ✅ |  ❌  |
| templates | TemplateID | No pagination | ✅ |  ❌  |
| people | EmailAddress | No pagination | ✅ |  ❌  |
| tags | Name | No pagination | ✅ |  ❌  |
| subscriber_lists | ListID | No pagination | ✅ |  ❌  |
| suppression_lists | EmailAddress | DefaultPaginator | ✅ |  ❌  |
| sent_campaigns | CampaignID | DefaultPaginator | ✅ |  ✅  |
| draft_campaigns | CampaignID | No pagination | ✅ |  ❌  |
| scheduled_campaigns | CampaignID  | No pagination | ✅ |  ❌  |

## Changelog

<details>
  <summary>Expand to review</summary>

| Version          | Date              | Pull Request | Subject        |
|------------------|-------------------|--------------|----------------|
| 0.0.1 | 2024-10-05 | | Initial release by [@aazam-gh](https://github.com/aazam-gh) via Connector Builder |

</details>

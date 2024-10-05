# Campaign Monitor
This is the setup guide for the Campaign Monitor source.

Campaign Monitor is an email marketing and services platform https://www.campaignmonitor.com/
This connector ingests a variety of endpoints from the Campaign Monitor API.
In order to use the API, you must first create an account. You can generate your API key in the account settings.
https://www.campaignmonitor.com/api/v3-3/getting-started/ 


## Configuration

| Input | Type | Description | Default Value |
|-------|------|-------------|---------------|
| `username` | `string` | Username.  |  |
| `password` | `string` | Password.  |  |
| `client_id` | `string` | Client ID. The specific ID of a client in your account |  |
| `start_date` | `string` | start_date. Date from when the sync should start |  |

## Streams
| Stream Name | Primary Key | Pagination | Supports Full Sync | Supports Incremental |
|-------------|-------------|------------|---------------------|----------------------|
| clients | ClientID | No pagination | ✅ |  ❌  |
| admins | EmailAddress | No pagination | ✅ |  ❌  |
| client_details |  | No pagination | ✅ |  ❌  |
| segments | SegmentID | No pagination | ✅ |  ❌  |
| templates | TemplateID | No pagination | ✅ |  ❌  |
| people | EmailAddress | No pagination | ✅ |  ❌  |
| tags | Name | No pagination | ✅ |  ❌  |
| subscriber_lists | ListID | No pagination | ✅ |  ❌  |
| suppression_lists | EmailAddress | DefaultPaginator | ✅ |  ❌  |
| sent_campaigns | CampaignID | DefaultPaginator | ✅ |  ✅  |
| draft_campaigns | CampaignID | No pagination | ✅ |  ❌  |
| scheduled_campaigns |  | No pagination | ✅ |  ❌  |

## Changelog

<details>
  <summary>Expand to review</summary>

| Version          | Date              | Pull Request | Subject        |
|------------------|-------------------|--------------|----------------|
| 0.0.1 | 2024-10-05 | | Initial release by [@aazam-gh](https://github.com/aazam-gh) via Connector Builder |

</details>

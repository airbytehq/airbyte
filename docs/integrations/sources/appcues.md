# Appcues
New Source: AppCues
Account ID link: https://studio.appcues.com/settings/account
Docs link: https://api.appcues.com/v2/docs
API keys link: https://studio.appcues.com/settings/keys

## Configuration

| Input | Type | Description | Default Value |
|-------|------|-------------|---------------|
| `username` | `string` | Username.  |  |
| `password` | `string` | Password.  |  |
| `account_id` | `string` | Account ID. Account ID of Appcues found in account settings page (https://studio.appcues.com/settings/account) |  |
| `start_date` | `string` | Start date.  |  |

## Streams
| Stream Name | Primary Key | Pagination | Supports Full Sync | Supports Incremental |
|-------------|-------------|------------|---------------------|----------------------|
| launchpads | id | No pagination | ✅ |  ✅  |
| flows | id | No pagination | ✅ |  ✅  |
| banners | id | No pagination | ✅ |  ✅  |
| checklists | id | No pagination | ✅ |  ✅  |
| pins | id | No pagination | ✅ |  ✅  |
| tags | id | No pagination | ✅ |  ✅  |
| segments | id | No pagination | ✅ |  ✅  |

## Changelog

<details>
  <summary>Expand to review</summary>

| Version          | Date       | Subject        |
|------------------|------------|----------------|
| 0.0.1 | 2024-09-03 | Initial release by [@btkcodedev](https://github.com/btkcodedev) via Connector Builder|

</details>
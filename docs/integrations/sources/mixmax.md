# MixMax
Website: https://app.mixmax.com/
API Docs: https://developer.mixmax.com/reference/getting-started-with-the-api
Auth Keys: https://app.mixmax.com/dashboard/settings/personal/integrations

## Configuration

| Input | Type | Description | Default Value |
|-------|------|-------------|---------------|
| `api_key` | `string` | API Key.  |  |
| `start_date` | `string` | Start date.  |  |

## Streams
| Stream Name | Primary Key | Pagination | Supports Full Sync | Supports Incremental |
|-------------|-------------|------------|---------------------|----------------------|
| appointmentlinks | userId | DefaultPaginator | ✅ |  ❌  |
| codesnippets | _id | DefaultPaginator | ✅ |  ✅  |
| insightsreports | _id | DefaultPaginator | ✅ |  ✅  |
| integrations_commands | _id | DefaultPaginator | ✅ |  ❌  |
| integrations_enhancements | _id | DefaultPaginator | ✅ |  ❌  |
| integrations_linkresolvers | _id | DefaultPaginator | ✅ |  ✅  |
| integrations_sidebars | _id | DefaultPaginator | ✅ |  ❌  |
| livefeed | uid | DefaultPaginator | ✅ |  ❌  |
| meetingtypes | _id | DefaultPaginator | ✅ |  ✅  |
| messages | _id | DefaultPaginator | ✅ |  ✅  |
| rules | _id | DefaultPaginator | ✅ |  ✅  |
| rules_actions | _id | DefaultPaginator | ✅ |  ✅  |
| sequences | _id | DefaultPaginator | ✅ |  ✅  |
| sequences_recipients | _id | DefaultPaginator | ✅ |  ✅  |
| sequencefolders | _id | DefaultPaginator | ✅ |  ✅  |
| snippettags | _id | DefaultPaginator | ✅ |  ✅  |
| snippettags_snippets | _id | DefaultPaginator | ✅ |  ✅  |
| userpreferences_me | _id | DefaultPaginator | ✅ |  ❌  |
| users_me | _id | DefaultPaginator | ✅ |  ❌  |

## Changelog

<details>
  <summary>Expand to review</summary>

| Version          | Date       | Subject        |
|------------------|------------|----------------|
| 0.0.1 | 2024-09-26 | Initial release by [@btkcodedev](https://github.com/btkcodedev) via Connector Builder|

</details>
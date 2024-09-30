# MixMax
This directory contains the manifest-only connector for [`source-mixmax`](https://app.mixmax.com/).

## Documentation reference:
Visit `https://developer.mixmax.com/reference/getting-started-with-the-api` for API documentation

## Authentication setup
`Mixmax` uses API key authentication, Visit `https://app.mixmax.com/dashboard/settings/personal/integrations` for getting your API keys.

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

| Version | Date | Pull Request | Subject |
| ------------------ | ------------ | --- | ---------------- |
| 0.0.1 | 2024-09-26 | [45921](https://github.com/airbytehq/airbyte/pull/45921) | Initial release by [@btkcodedev](https://github.com/btkcodedev) via Connector Builder |

</details>
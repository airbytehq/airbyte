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
| 0.0.10 | 2025-01-11 | [51209](https://github.com/airbytehq/airbyte/pull/51209) | Update dependencies |
| 0.0.9 | 2024-12-28 | [50605](https://github.com/airbytehq/airbyte/pull/50605) | Update dependencies |
| 0.0.8 | 2024-12-21 | [50105](https://github.com/airbytehq/airbyte/pull/50105) | Update dependencies |
| 0.0.7 | 2024-12-14 | [49604](https://github.com/airbytehq/airbyte/pull/49604) | Update dependencies |
| 0.0.6 | 2024-12-12 | [49267](https://github.com/airbytehq/airbyte/pull/49267) | Update dependencies |
| 0.0.5 | 2024-12-11 | [48986](https://github.com/airbytehq/airbyte/pull/48986) | Starting with this version, the Docker image is now rootless. Please note that this and future versions will not be compatible with Airbyte versions earlier than 0.64 |
| 0.0.4 | 2024-11-04 | [48160](https://github.com/airbytehq/airbyte/pull/48160) | Update dependencies |
| 0.0.3 | 2024-10-29 | [47838](https://github.com/airbytehq/airbyte/pull/47838) | Update dependencies |
| 0.0.2 | 2024-10-28 | [47578](https://github.com/airbytehq/airbyte/pull/47578) | Update dependencies |
| 0.0.1 | 2024-09-26 | [45921](https://github.com/airbytehq/airbyte/pull/45921) | Initial release by [@btkcodedev](https://github.com/btkcodedev) via Connector Builder |

</details>

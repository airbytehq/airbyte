# Shortcut
This page contains the setup guide and reference information for the [Shortcut](https://app.shortcut.com/) source connector.

## Prerequisites
To set up the shortcut source connector with Airbyte, you'll need to create your API tokens from theie settings page. Please visit `https://app.shortcut.com/janfab/settings/account/api-tokens` for getting your api_key.

## Documentation reference:
Visit `https://developer.shortcut.com/api/rest/v3#Introduction` for API documentation

## Authentication setup
Refer `https://developer.shortcut.com/api/rest/v3#Authentication` for more details.

## Configuration

| Input | Type | Description | Default Value |
|-------|------|-------------|---------------|
| `api_key_2` | `string` | API Key.  |  |
| `start_date` | `string` | Start date.  |  |
| `query` | `string` | Query. Query for searching as defined in `https://help.shortcut.com/hc/en-us/articles/360000046646-Searching-in-Shortcut-Using-Search-Operators` | title:Our first Epic |

## Streams
| Stream Name | Primary Key | Pagination | Supports Full Sync | Supports Incremental |
|-------------|-------------|------------|---------------------|----------------------|
| search_epics | id | DefaultPaginator | ✅ |  ✅  |
| categories | id | No pagination | ✅ |  ✅  |
| categories_milestones | id | No pagination | ✅ |  ✅  |
| categories_objectives | id | No pagination | ✅ |  ✅  |
| custom-fields | id | No pagination | ✅ |  ✅  |
| epic-workflow | id | No pagination | ✅ |  ✅  |
| epics | id | No pagination | ✅ |  ✅  |
| epics_comments | id | No pagination | ✅ |  ✅  |
| epics_stories | id | No pagination | ✅ |  ✅  |
| files | id | No pagination | ✅ |  ✅  |
| groups | id | No pagination | ✅ |  ❌  |
| groups_stories | id | No pagination | ✅ |  ✅  |
| iterations | id | No pagination | ✅ |  ✅  |
| iterations_stories | id | No pagination | ✅ |  ✅  |
| labels | id | No pagination | ✅ |  ✅  |
| member | id | No pagination | ✅ |  ❌  |
| members | id | No pagination | ✅ |  ✅  |
| milestones | id | No pagination | ✅ |  ✅  |
| milestones_epics | id | No pagination | ✅ |  ✅  |
| objectives | id | No pagination | ✅ |  ✅  |
| objectives_epics | id | No pagination | ✅ |  ✅  |
| workflows | id | No pagination | ✅ |  ✅  |
| stories_comments | id | No pagination | ✅ |  ✅  |
| story_history | id | No pagination | ✅ |  ✅  |

## Changelog

<details>
  <summary>Expand to review</summary>

| Version | Date | Pull Request | Subject |
| ------------------ | ------------ | --- | ---------------- |
| 0.0.1 | 2024-09-05 | [45176](https://github.com/airbytehq/airbyte/pull/45176) | Initial release by [@btkcodedev](https://github.com/btkcodedev) via Connector Builder |

</details>

# Height

This page contains the setup guide and reference information for the Height source connector.

## Prerequisites

To set up the Height source connector, you'll need the Height API key that you could see once you login and navigate to https://height.app/xxxxx/settings/api, and copy your secret key
Website: https://height.app

API Documentation: https://height.notion.site/API-documentation-643aea5bf01742de9232e5971cb4afda

## Configuration

| Input | Type | Description | Default Value |
|-------|------|-------------|---------------|
| `api_key` | `string` | API secret which is copied from the settings page of height.app  |  |
| `start_date` | `string` | Start date for incremental sync supported streams |  |
| `search_query` | `string` | search_query. Search query to be used with search stream | task |

## Streams

| Stream Name | Primary Key | Pagination | Supports Full Sync | Supports Incremental |
|-------------|-------------|------------|---------------------|----------------------|
| workspace | id | No pagination | ✅ |  ✅  |
| lists | id | No pagination | ✅ |  ✅  |
| tasks | id | No pagination | ✅ |  ✅  |
| activities | id | No pagination | ✅ |  ✅  |
| field_templates | id | No pagination | ✅ |  ❌  |
| users | id | No pagination | ✅ |  ✅  |
| groups | id | No pagination | ✅ |  ✅  |
| search | id | No pagination | ✅ |  ✅  |

## Changelog

<details>
  <summary>Expand to review</summary>

| Version | Date | Pull Request | Subject |
| ------------------ | ------------ | ---- | ---------------- |
| 0.0.1 | 2024-08-31 | [45065](https://github.com/airbytehq/airbyte/pull/45065) | Initial release by [@btkcodedev](https://github.com/btkcodedev) via Connector Builder |

</details>
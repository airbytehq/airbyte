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
| 0.0.14 | 2025-02-08 | [53247](https://github.com/airbytehq/airbyte/pull/53247) | Update dependencies |
| 0.0.13 | 2025-02-01 | [52741](https://github.com/airbytehq/airbyte/pull/52741) | Update dependencies |
| 0.0.12 | 2025-01-25 | [52264](https://github.com/airbytehq/airbyte/pull/52264) | Update dependencies |
| 0.0.11 | 2025-01-18 | [51836](https://github.com/airbytehq/airbyte/pull/51836) | Update dependencies |
| 0.0.10 | 2025-01-11 | [51154](https://github.com/airbytehq/airbyte/pull/51154) | Update dependencies |
| 0.0.9 | 2024-12-28 | [50610](https://github.com/airbytehq/airbyte/pull/50610) | Update dependencies |
| 0.0.8 | 2024-12-21 | [50094](https://github.com/airbytehq/airbyte/pull/50094) | Update dependencies |
| 0.0.7 | 2024-12-14 | [49597](https://github.com/airbytehq/airbyte/pull/49597) | Update dependencies |
| 0.0.6 | 2024-12-12 | [49225](https://github.com/airbytehq/airbyte/pull/49225) | Update dependencies |
| 0.0.5 | 2024-12-11 | [48977](https://github.com/airbytehq/airbyte/pull/48977) | Starting with this version, the Docker image is now rootless. Please note that this and future versions will not be compatible with Airbyte versions earlier than 0.64 |
| 0.0.4 | 2024-11-04 | [48158](https://github.com/airbytehq/airbyte/pull/48158) | Update dependencies |
| 0.0.3 | 2024-10-29 | [47790](https://github.com/airbytehq/airbyte/pull/47790) | Update dependencies |
| 0.0.2 | 2024-10-28 | [47615](https://github.com/airbytehq/airbyte/pull/47615) | Update dependencies |
| 0.0.1 | 2024-08-31 | [45065](https://github.com/airbytehq/airbyte/pull/45065) | Initial release by [@btkcodedev](https://github.com/btkcodedev) via Connector Builder |

</details>

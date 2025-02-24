# Piwik
This page contains the setup guide and reference information for the [Piwik](https://piwik.pro/) source connector.

## Documentation reference:
Visit `https://developers.piwik.pro/en/latest/platform/getting_started.html` for API documentation

## Authentication setup
`Source-piwik` uses OAuth2.0 - Client credentials authentication,
Visit `https://developers.piwik.pro/en/latest/platform/getting_started.html#generate-api-credentials` for getting credentials for OAuth2.0

## Configuration

| Input | Type | Description | Default Value |
|-------|------|-------------|---------------|
| `client_id` | `string` | Client ID.  |  |
| `client_secret` | `string` | Client secret.  |  |
| `organization_id` | `string` | Organization ID. The organization id appearing at URL of your piwik website |  |

## Streams
| Stream Name | Primary Key | Pagination | Supports Full Sync | Supports Incremental |
|-------------|-------------|------------|---------------------|----------------------|
| users | id | DefaultPaginator | ✅ |  ❌  |
| users-me | id | DefaultPaginator | ✅ |  ❌  |
| user-groups | id | DefaultPaginator | ✅ |  ❌  |
| tracker_settings | id | DefaultPaginator | ✅ |  ❌  |
| modules | id | DefaultPaginator | ✅ |  ❌  |
| meta-sites | id | DefaultPaginator | ✅ |  ❌  |
| meta-sites_apps | id | DefaultPaginator | ✅ |  ❌  |
| meta-sites_apps-with-meta-sites | id | DefaultPaginator | ✅ |  ❌  |
| container-settings_settings |  | DefaultPaginator | ✅ |  ❌  |
| apps | id | DefaultPaginator | ✅ |  ❌  |
| audit-log_entries | id | DefaultPaginator | ✅ |  ❌  |
| apps_details | id | DefaultPaginator | ✅ |  ❌  |
| access-control_actions | id | DefaultPaginator | ✅ |  ❌  |
| access-control_meta-site_permission_user | uid | DefaultPaginator | ✅ |  ❌  |

## Changelog

<details>
  <summary>Expand to review</summary>

| Version | Date | Pull Request | Subject |
| ------------------ | ------------ | --- | ---------------- |
| 0.0.16 | 2025-02-23 | [54553](https://github.com/airbytehq/airbyte/pull/54553) | Update dependencies |
| 0.0.15 | 2025-02-15 | [53958](https://github.com/airbytehq/airbyte/pull/53958) | Update dependencies |
| 0.0.14 | 2025-02-08 | [53509](https://github.com/airbytehq/airbyte/pull/53509) | Update dependencies |
| 0.0.13 | 2025-02-01 | [53013](https://github.com/airbytehq/airbyte/pull/53013) | Update dependencies |
| 0.0.12 | 2025-01-25 | [52515](https://github.com/airbytehq/airbyte/pull/52515) | Update dependencies |
| 0.0.11 | 2025-01-18 | [51926](https://github.com/airbytehq/airbyte/pull/51926) | Update dependencies |
| 0.0.10 | 2025-01-11 | [51365](https://github.com/airbytehq/airbyte/pull/51365) | Update dependencies |
| 0.0.9 | 2024-12-28 | [50744](https://github.com/airbytehq/airbyte/pull/50744) | Update dependencies |
| 0.0.8 | 2024-12-21 | [50253](https://github.com/airbytehq/airbyte/pull/50253) | Update dependencies |
| 0.0.7 | 2024-12-14 | [49728](https://github.com/airbytehq/airbyte/pull/49728) | Update dependencies |
| 0.0.6 | 2024-12-12 | [49356](https://github.com/airbytehq/airbyte/pull/49356) | Update dependencies |
| 0.0.5 | 2024-12-11 | [49103](https://github.com/airbytehq/airbyte/pull/49103) | Starting with this version, the Docker image is now rootless. Please note that this and future versions will not be compatible with Airbyte versions earlier than 0.64 |
| 0.0.4 | 2024-11-04 | [48305](https://github.com/airbytehq/airbyte/pull/48305) | Update dependencies |
| 0.0.3 | 2024-10-29 | [47931](https://github.com/airbytehq/airbyte/pull/47931) | Update dependencies |
| 0.0.2 | 2024-10-28 | [47569](https://github.com/airbytehq/airbyte/pull/47569) | Update dependencies |
| 0.0.1 | 2024-09-14 | [45586](https://github.com/airbytehq/airbyte/pull/45586) | Initial release by [@btkcodedev](https://github.com/btkcodedev) via Connector Builder |

</details>

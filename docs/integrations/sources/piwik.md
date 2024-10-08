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
| 0.0.1 | 2024-09-14 | [45586](https://github.com/airbytehq/airbyte/pull/45586) | Initial release by [@btkcodedev](https://github.com/btkcodedev) via Connector Builder |

</details>
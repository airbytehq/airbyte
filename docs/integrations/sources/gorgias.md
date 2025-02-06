# Gorgias
This directory contains the manifest-only connector for [`source-gorgias`](https://gorgias.com/).

## Documentation reference:
Visit `https://developers.gorgias.com/reference/introduction` for API documentation

## Authentication setup
`Gorgias` uses Http basic authentication, Visit `https://YOUR_DOMAIN.gorgias.com/app/settings/api` for getting your username and password. Visit `https://developers.gorgias.com/reference/authentication` for more information.

## Configuration

| Input | Type | Description | Default Value |
|-------|------|-------------|---------------|
| `username` | `string` | Username.  |  |
| `password` | `string` | Password.  |  |
| `domain_name` | `string` | Domain name. Domain name given for gorgias, found as your url prefix for accessing your website |  |
| `start_date` | `string` | Start date.  |  |

## Streams
| Stream Name | Primary Key | Pagination | Supports Full Sync | Supports Incremental |
|-------------|-------------|------------|---------------------|----------------------|
| account | domain | No pagination | ✅ |  ✅  |
| customers | id | DefaultPaginator | ✅ |  ✅  |
| custom-fields | id | DefaultPaginator | ✅ |  ✅  |
| events | id | DefaultPaginator | ✅ |  ✅  |
| integrations | id | DefaultPaginator | ✅ |  ✅  |
| jobs | id | DefaultPaginator | ✅ |  ✅  |
| macros | id | DefaultPaginator | ✅ |  ✅  |
| views | id | DefaultPaginator | ✅ |  ✅  |
| rules | id | DefaultPaginator | ✅ |  ✅  |
| satisfaction-surveys | id | DefaultPaginator | ✅ |  ✅  |
| tags | id | DefaultPaginator | ✅ |  ✅  |
| teams | id | DefaultPaginator | ✅ |  ✅  |
| tickets | id | DefaultPaginator | ✅ |  ✅  |
| messages | id | DefaultPaginator | ✅ |  ✅  |
| users | id | DefaultPaginator | ✅ |  ✅  |
| views_items | id | DefaultPaginator | ✅ |  ✅  |

## Changelog

<details>
  <summary>Expand to review</summary>

| Version | Date | Pull Request | Subject |
| ------------------ | ------------ | --- | ---------------- |
| 0.1.0 | 2025-01-30 | [52637](https://github.com/airbytehq/airbyte/pull/52637) | Add retries for rate limited streams |
| 0.0.8 | 2024-12-23 | [49935](https://github.com/airbytehq/airbyte/pull/49935) | Add additional cursor datetime format |
| 0.0.7 | 2024-12-21 | [50123](https://github.com/airbytehq/airbyte/pull/50123) | Update dependencies |
| 0.0.6 | 2024-12-14 | [49219](https://github.com/airbytehq/airbyte/pull/49219) | Update dependencies |
| 0.0.5 | 2024-12-11 | [48973](https://github.com/airbytehq/airbyte/pull/48973) | Starting with this version, the Docker image is now rootless. Please note that this and future versions will not be compatible with Airbyte versions earlier than 0.64 |
| 0.0.4 | 2024-11-06 | [48378](https://github.com/airbytehq/airbyte/pull/48378) | Fix incremental sync format, Auto update schema with additional fields |
| 0.0.3 | 2024-10-29 | [47923](https://github.com/airbytehq/airbyte/pull/47923) | Update dependencies |
| 0.0.2 | 2024-10-28 | [47459](https://github.com/airbytehq/airbyte/pull/47459) | Update dependencies |
| 0.0.1 | 2024-09-29 | [46221](https://github.com/airbytehq/airbyte/pull/46221) | Initial release by [@btkcodedev](https://github.com/btkcodedev) via Connector Builder |

</details>

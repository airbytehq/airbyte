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
| 0.1.32 | 2025-12-09 | [70485](https://github.com/airbytehq/airbyte/pull/70485) | Update dependencies |
| 0.1.31 | 2025-11-25 | [70062](https://github.com/airbytehq/airbyte/pull/70062) | Update dependencies |
| 0.1.30 | 2025-11-18 | [69410](https://github.com/airbytehq/airbyte/pull/69410) | Update dependencies |
| 0.1.29 | 2025-10-29 | [68809](https://github.com/airbytehq/airbyte/pull/68809) | Update dependencies |
| 0.1.28 | 2025-10-21 | [68243](https://github.com/airbytehq/airbyte/pull/68243) | Update dependencies |
| 0.1.27 | 2025-10-14 | [67919](https://github.com/airbytehq/airbyte/pull/67919) | Update dependencies |
| 0.1.26 | 2025-10-07 | [67412](https://github.com/airbytehq/airbyte/pull/67412) | Update dependencies |
| 0.1.25 | 2025-09-30 | [66399](https://github.com/airbytehq/airbyte/pull/66399) | Update dependencies |
| 0.1.24 | 2025-09-09 | [66058](https://github.com/airbytehq/airbyte/pull/66058) | Update dependencies |
| 0.1.23 | 2025-08-23 | [65350](https://github.com/airbytehq/airbyte/pull/65350) | Update dependencies |
| 0.1.22 | 2025-08-09 | [64599](https://github.com/airbytehq/airbyte/pull/64599) | Update dependencies |
| 0.1.21 | 2025-08-02 | [64303](https://github.com/airbytehq/airbyte/pull/64303) | Update dependencies |
| 0.1.20 | 2025-07-26 | [63845](https://github.com/airbytehq/airbyte/pull/63845) | Update dependencies |
| 0.1.19 | 2025-07-19 | [63487](https://github.com/airbytehq/airbyte/pull/63487) | Update dependencies |
| 0.1.18 | 2025-07-12 | [63114](https://github.com/airbytehq/airbyte/pull/63114) | Update dependencies |
| 0.1.17 | 2025-07-05 | [62553](https://github.com/airbytehq/airbyte/pull/62553) | Update dependencies |
| 0.1.16 | 2025-06-28 | [62193](https://github.com/airbytehq/airbyte/pull/62193) | Update dependencies |
| 0.1.15 | 2025-06-21 | [61810](https://github.com/airbytehq/airbyte/pull/61810) | Update dependencies |
| 0.1.14 | 2025-06-14 | [61147](https://github.com/airbytehq/airbyte/pull/61147) | Update dependencies |
| 0.1.13 | 2025-05-24 | [60609](https://github.com/airbytehq/airbyte/pull/60609) | Update dependencies |
| 0.1.12 | 2025-05-10 | [59874](https://github.com/airbytehq/airbyte/pull/59874) | Update dependencies |
| 0.1.11 | 2025-05-03 | [59240](https://github.com/airbytehq/airbyte/pull/59240) | Update dependencies |
| 0.1.10 | 2025-04-26 | [58770](https://github.com/airbytehq/airbyte/pull/58770) | Update dependencies |
| 0.1.9 | 2025-04-19 | [58193](https://github.com/airbytehq/airbyte/pull/58193) | Update dependencies |
| 0.1.8 | 2025-04-12 | [57708](https://github.com/airbytehq/airbyte/pull/57708) | Update dependencies |
| 0.1.7 | 2025-04-05 | [57041](https://github.com/airbytehq/airbyte/pull/57041) | Update dependencies |
| 0.1.6 | 2025-03-29 | [56719](https://github.com/airbytehq/airbyte/pull/56719) | Update dependencies |
| 0.1.5 | 2025-03-22 | [56041](https://github.com/airbytehq/airbyte/pull/56041) | Update dependencies |
| 0.1.4 | 2025-03-08 | [55491](https://github.com/airbytehq/airbyte/pull/55491) | Update dependencies |
| 0.1.3 | 2025-03-01 | [54794](https://github.com/airbytehq/airbyte/pull/54794) | Update dependencies |
| 0.1.2 | 2025-02-22 | [54335](https://github.com/airbytehq/airbyte/pull/54335) | Update dependencies |
| 0.1.1 | 2025-02-15 | [50638](https://github.com/airbytehq/airbyte/pull/50638) | Update dependencies |
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

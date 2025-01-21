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
| 0.0.1 | 2024-09-29 | [46221](https://github.com/airbytehq/airbyte/pull/46221) | Initial release by [@btkcodedev](https://github.com/btkcodedev) via Connector Builder |

</details>
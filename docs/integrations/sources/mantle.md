# Mantle
This connector use the Mantle API to get customers and subscriptions streams

## Configuration

| Input | Type | Description | Default Value |
|-------|------|-------------|---------------|
| `api_key` | `string` | API Key.  |  |
| `start_date` | `string` | Start date.  |  |

## Streams
| Stream Name | Primary Key | Pagination | Supports Full Sync | Supports Incremental |
|-------------|-------------|------------|---------------------|----------------------|
| customers | id | DefaultPaginator | ✅ |  ✅  |
| subscriptions | id | DefaultPaginator | ✅ |  ✅  |

## IP allow list

If you use Airbyte Cloud and your organization restricts access to specific IPs, add the [Airbyte Cloud IP addresses](https://docs.airbyte.com/platform/operating-airbyte/ip-allowlist) to your allow list.

## Changelog

<details>
  <summary>Expand to review</summary>

| Version          | Date              | Pull Request | Subject        |
|------------------|-------------------|--------------|----------------|
| 0.0.28 | 2026-07-21 | [82481](https://github.com/airbytehq/airbyte/pull/82481) | Update dependencies |
| 0.0.27 | 2026-07-14 | [81892](https://github.com/airbytehq/airbyte/pull/81892) | Update dependencies |
| 0.0.26 | 2026-06-30 | [81143](https://github.com/airbytehq/airbyte/pull/81143) | Update dependencies |
| 0.0.25 | 2026-06-23 | [80533](https://github.com/airbytehq/airbyte/pull/80533) | Update dependencies |
| 0.0.24 | 2026-06-16 | [79959](https://github.com/airbytehq/airbyte/pull/79959) | Update dependencies |
| 0.0.23 | 2026-06-09 | [79406](https://github.com/airbytehq/airbyte/pull/79406) | Update dependencies |
| 0.0.22 | 2026-06-02 | [78824](https://github.com/airbytehq/airbyte/pull/78824) | Update dependencies |
| 0.0.21 | 2026-04-28 | [77359](https://github.com/airbytehq/airbyte/pull/77359) | Update dependencies |
| 0.0.20 | 2026-04-21 | [76687](https://github.com/airbytehq/airbyte/pull/76687) | Update dependencies |
| 0.0.19 | 2026-03-31 | [75810](https://github.com/airbytehq/airbyte/pull/75810) | Update dependencies |
| 0.0.18 | 2026-03-17 | [73821](https://github.com/airbytehq/airbyte/pull/73821) | Update dependencies |
| 0.0.17 | 2026-02-17 | [73394](https://github.com/airbytehq/airbyte/pull/73394) | Update dependencies |
| 0.0.16 | 2026-02-10 | [73189](https://github.com/airbytehq/airbyte/pull/73189) | Update dependencies |
| 0.0.15 | 2026-02-03 | [72724](https://github.com/airbytehq/airbyte/pull/72724) | Update dependencies |
| 0.0.14 | 2026-01-20 | [72009](https://github.com/airbytehq/airbyte/pull/72009) | Update dependencies |
| 0.0.13 | 2026-01-14 | [71544](https://github.com/airbytehq/airbyte/pull/71544) | Update dependencies |
| 0.0.12 | 2025-12-18 | [70750](https://github.com/airbytehq/airbyte/pull/70750) | Update dependencies |
| 0.0.11 | 2025-11-25 | [70132](https://github.com/airbytehq/airbyte/pull/70132) | Update dependencies |
| 0.0.10 | 2025-11-18 | [69545](https://github.com/airbytehq/airbyte/pull/69545) | Update dependencies |
| 0.0.9 | 2025-10-29 | [69069](https://github.com/airbytehq/airbyte/pull/69069) | Update dependencies |
| 0.0.8 | 2025-10-21 | [68445](https://github.com/airbytehq/airbyte/pull/68445) | Update dependencies |
| 0.0.7 | 2025-10-14 | [67809](https://github.com/airbytehq/airbyte/pull/67809) | Update dependencies |
| 0.0.6 | 2025-10-07 | [67377](https://github.com/airbytehq/airbyte/pull/67377) | Update dependencies |
| 0.0.5 | 2025-09-30 | [66339](https://github.com/airbytehq/airbyte/pull/66339) | Update dependencies |
| 0.0.4 | 2025-09-09 | [65746](https://github.com/airbytehq/airbyte/pull/65746) | Update dependencies |
| 0.0.3 | 2025-09-07 | [65150](https://github.com/airbytehq/airbyte/pull/65150) | Fix pagination for Subscriptions |
| 0.0.2 | 2025-08-23 | [65182](https://github.com/airbytehq/airbyte/pull/65182) | Update dependencies |
| 0.0.1 | 2025-08-13 | | Initial release by [@KimPlv](https://github.com/KimPlv) via Connector Builder |

</details>

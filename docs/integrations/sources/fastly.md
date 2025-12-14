# Fastly
Website: https://manage.fastly.com/
API Reference: https://www.fastly.com/documentation/reference/api/

## Configuration

| Input | Type | Description | Default Value |
|-------|------|-------------|---------------|
| `fastly_api_token` | `string` | Fastly API Token. Your Fastly API token. You can generate this token in the Fastly web interface under Account Settings or via the Fastly API. Ensure the token has the appropriate scope for your use case. |  |
| `start_date` | `string` | Start date.  |  |

## Streams
| Stream Name | Primary Key | Pagination | Supports Full Sync | Supports Incremental |
|-------------|-------------|------------|---------------------|----------------------|
| current_user | id | No pagination | ✅ |  ✅  |
| service | id | DefaultPaginator | ✅ |  ✅  |
| service_details | id | DefaultPaginator | ✅ |  ✅  |
| service_version | uuid | DefaultPaginator | ✅ |  ✅  |
| service_dictionaries | id | DefaultPaginator | ✅ |  ✅  |
| service_backend | uuid | DefaultPaginator | ✅ |  ✅  |
| service_domain | uuid | DefaultPaginator | ✅ |  ✅  |
| service_acl | uuid | DefaultPaginator | ✅ |  ✅  |

## Changelog

<details>
  <summary>Expand to review</summary>

| Version          | Date              | Pull Request | Subject        |
|------------------|-------------------|--------------|----------------|
| 0.0.25 | 2025-12-09 | [70551](https://github.com/airbytehq/airbyte/pull/70551) | Update dependencies |
| 0.0.24 | 2025-11-25 | [70178](https://github.com/airbytehq/airbyte/pull/70178) | Update dependencies |
| 0.0.23 | 2025-11-18 | [69424](https://github.com/airbytehq/airbyte/pull/69424) | Update dependencies |
| 0.0.22 | 2025-10-29 | [68704](https://github.com/airbytehq/airbyte/pull/68704) | Update dependencies |
| 0.0.21 | 2025-10-21 | [68558](https://github.com/airbytehq/airbyte/pull/68558) | Update dependencies |
| 0.0.20 | 2025-10-14 | [67753](https://github.com/airbytehq/airbyte/pull/67753) | Update dependencies |
| 0.0.19 | 2025-10-07 | [67288](https://github.com/airbytehq/airbyte/pull/67288) | Update dependencies |
| 0.0.18 | 2025-09-30 | [66283](https://github.com/airbytehq/airbyte/pull/66283) | Update dependencies |
| 0.0.17 | 2025-09-09 | [65836](https://github.com/airbytehq/airbyte/pull/65836) | Update dependencies |
| 0.0.16 | 2025-08-23 | [65249](https://github.com/airbytehq/airbyte/pull/65249) | Update dependencies |
| 0.0.15 | 2025-08-09 | [64800](https://github.com/airbytehq/airbyte/pull/64800) | Update dependencies |
| 0.0.14 | 2025-08-02 | [64392](https://github.com/airbytehq/airbyte/pull/64392) | Update dependencies |
| 0.0.13 | 2025-07-26 | [64036](https://github.com/airbytehq/airbyte/pull/64036) | Update dependencies |
| 0.0.12 | 2025-07-19 | [63577](https://github.com/airbytehq/airbyte/pull/63577) | Update dependencies |
| 0.0.11 | 2025-07-12 | [63009](https://github.com/airbytehq/airbyte/pull/63009) | Update dependencies |
| 0.0.10 | 2025-07-05 | [62776](https://github.com/airbytehq/airbyte/pull/62776) | Update dependencies |
| 0.0.9 | 2025-06-28 | [62317](https://github.com/airbytehq/airbyte/pull/62317) | Update dependencies |
| 0.0.8 | 2025-06-21 | [61972](https://github.com/airbytehq/airbyte/pull/61972) | Update dependencies |
| 0.0.7 | 2025-06-14 | [61192](https://github.com/airbytehq/airbyte/pull/61192) | Update dependencies |
| 0.0.6 | 2025-05-24 | [60388](https://github.com/airbytehq/airbyte/pull/60388) | Update dependencies |
| 0.0.5 | 2025-05-10 | [59407](https://github.com/airbytehq/airbyte/pull/59407) | Update dependencies |
| 0.0.4 | 2025-04-26 | [58831](https://github.com/airbytehq/airbyte/pull/58831) | Update dependencies |
| 0.0.3 | 2025-04-19 | [58337](https://github.com/airbytehq/airbyte/pull/58337) | Update dependencies |
| 0.0.2 | 2025-04-12 | [57843](https://github.com/airbytehq/airbyte/pull/57843) | Update dependencies |
| 0.0.1 | 2025-04-09 | [57528](https://github.com/airbytehq/airbyte/pull/57528) | Initial release by [@btkcodedev](https://github.com/btkcodedev) via Connector Builder |

</details>

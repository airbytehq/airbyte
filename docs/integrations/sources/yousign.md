# YouSign
Website: https://yousign.app/
API Reference: https://developers.yousign.com/reference/oas-specification

## Configuration

| Input | Type | Description | Default Value |
|-------|------|-------------|---------------|
| `api_key` | `string` | API Key. API key or access token |  |
| `subdomain` | `string` | Subdomain. The subdomain for the Yousign API environment, such as &#39;sandbox&#39; or &#39;api&#39;. | api |
| `limit` | `string` | Limit. Limit for each response objects | 10 |
| `start_date` | `string` | Start date.  |  |

## Streams
| Stream Name | Primary Key | Pagination | Supports Full Sync | Supports Incremental |
|-------------|-------------|------------|---------------------|----------------------|
| signature_requests | id | DefaultPaginator | ✅ |  ✅  |
| signature_requests_followers | email | DefaultPaginator | ✅ |  ❌  |
| contacts | id | DefaultPaginator | ✅ |  ✅  |
| users | id | DefaultPaginator | ✅ |  ✅  |
| workspaces | id | DefaultPaginator | ✅ |  ✅  |
| electronic_seal_images | id | DefaultPaginator | ✅ |  ✅  |
| templates | id | DefaultPaginator | ✅ |  ✅  |
| labels | id | DefaultPaginator | ✅ |  ✅  |

## Changelog

<details>
  <summary>Expand to review</summary>

| Version          | Date              | Pull Request | Subject        |
|------------------|-------------------|--------------|----------------|
| 0.0.28 | 2025-12-09 | [70675](https://github.com/airbytehq/airbyte/pull/70675) | Update dependencies |
| 0.0.27 | 2025-11-25 | [70099](https://github.com/airbytehq/airbyte/pull/70099) | Update dependencies |
| 0.0.26 | 2025-11-18 | [69565](https://github.com/airbytehq/airbyte/pull/69565) | Update dependencies |
| 0.0.25 | 2025-10-29 | [68960](https://github.com/airbytehq/airbyte/pull/68960) | Update dependencies |
| 0.0.24 | 2025-10-21 | [68435](https://github.com/airbytehq/airbyte/pull/68435) | Update dependencies |
| 0.0.23 | 2025-10-14 | [68009](https://github.com/airbytehq/airbyte/pull/68009) | Update dependencies |
| 0.0.22 | 2025-10-07 | [67249](https://github.com/airbytehq/airbyte/pull/67249) | Update dependencies |
| 0.0.21 | 2025-09-30 | [66851](https://github.com/airbytehq/airbyte/pull/66851) | Update dependencies |
| 0.0.20 | 2025-09-24 | [66465](https://github.com/airbytehq/airbyte/pull/66465) | Update dependencies |
| 0.0.19 | 2025-09-09 | [65741](https://github.com/airbytehq/airbyte/pull/65741) | Update dependencies |
| 0.0.18 | 2025-08-24 | [65444](https://github.com/airbytehq/airbyte/pull/65444) | Update dependencies |
| 0.0.17 | 2025-08-09 | [64852](https://github.com/airbytehq/airbyte/pull/64852) | Update dependencies |
| 0.0.16 | 2025-08-02 | [64402](https://github.com/airbytehq/airbyte/pull/64402) | Update dependencies |
| 0.0.15 | 2025-07-26 | [64075](https://github.com/airbytehq/airbyte/pull/64075) | Update dependencies |
| 0.0.14 | 2025-07-20 | [63688](https://github.com/airbytehq/airbyte/pull/63688) | Update dependencies |
| 0.0.13 | 2025-07-12 | [63169](https://github.com/airbytehq/airbyte/pull/63169) | Update dependencies |
| 0.0.12 | 2025-07-05 | [62714](https://github.com/airbytehq/airbyte/pull/62714) | Update dependencies |
| 0.0.11 | 2025-06-28 | [62242](https://github.com/airbytehq/airbyte/pull/62242) | Update dependencies |
| 0.0.10 | 2025-06-21 | [61770](https://github.com/airbytehq/airbyte/pull/61770) | Update dependencies |
| 0.0.9 | 2025-06-15 | [61180](https://github.com/airbytehq/airbyte/pull/61180) | Update dependencies |
| 0.0.8 | 2025-05-24 | [60737](https://github.com/airbytehq/airbyte/pull/60737) | Update dependencies |
| 0.0.7 | 2025-05-10 | [59977](https://github.com/airbytehq/airbyte/pull/59977) | Update dependencies |
| 0.0.6 | 2025-05-04 | [59534](https://github.com/airbytehq/airbyte/pull/59534) | Update dependencies |
| 0.0.5 | 2025-04-26 | [58953](https://github.com/airbytehq/airbyte/pull/58953) | Update dependencies |
| 0.0.4 | 2025-04-19 | [58569](https://github.com/airbytehq/airbyte/pull/58569) | Update dependencies |
| 0.0.3 | 2025-04-13 | [58043](https://github.com/airbytehq/airbyte/pull/58043) | Update dependencies |
| 0.0.2 | 2025-04-05 | [57376](https://github.com/airbytehq/airbyte/pull/57376) | Update dependencies |
| 0.0.1 | 2025-04-01 | [56951](https://github.com/airbytehq/airbyte/pull/56951) | Initial release by [@btkcodedev](https://github.com/btkcodedev) via Connector Builder |

</details>

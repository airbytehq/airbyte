# GoLogin
Website: https://app.gologin.com/
Postman API Reference: https://documenter.getpostman.com/view/21126834/Uz5GnvaL#intro

## Configuration

| Input | Type | Description | Default Value |
|-------|------|-------------|---------------|
| `api_key` | `string` | API Key. API Key found at `https://app.gologin.com/personalArea/TokenApi` |  |
| `start_date` | `string` | Start date.  |  |

## Streams
| Stream Name | Primary Key | Pagination | Supports Full Sync | Supports Incremental |
|-------------|-------------|------------|---------------------|----------------------|
| profiles | id | DefaultPaginator | ✅ |  ✅  |
| browser_history | id | DefaultPaginator | ✅ |  ✅  |
| browser_cookies | uuid | DefaultPaginator | ✅ |  ✅  |
| folders | id | DefaultPaginator | ✅ |  ❌  |
| tags | _id | DefaultPaginator | ✅ |  ❌  |
| user | _id | DefaultPaginator | ✅ |  ✅  |
| user_metadata | _id | DefaultPaginator | ✅ |  ✅  |
| user_balance | uuid | DefaultPaginator | ✅ |  ❌  |
| user_timezones | uuid | DefaultPaginator | ✅ |  ❌  |

## Changelog

<details>
  <summary>Expand to review</summary>

| Version          | Date              | Pull Request | Subject        |
|------------------|-------------------|--------------|----------------|
| 0.0.25 | 2025-12-09 | [70670](https://github.com/airbytehq/airbyte/pull/70670) | Update dependencies |
| 0.0.24 | 2025-11-25 | [69898](https://github.com/airbytehq/airbyte/pull/69898) | Update dependencies |
| 0.0.23 | 2025-11-18 | [69401](https://github.com/airbytehq/airbyte/pull/69401) | Update dependencies |
| 0.0.22 | 2025-10-29 | [69028](https://github.com/airbytehq/airbyte/pull/69028) | Update dependencies |
| 0.0.21 | 2025-10-21 | [68301](https://github.com/airbytehq/airbyte/pull/68301) | Update dependencies |
| 0.0.20 | 2025-10-14 | [68018](https://github.com/airbytehq/airbyte/pull/68018) | Update dependencies |
| 0.0.19 | 2025-10-07 | [67253](https://github.com/airbytehq/airbyte/pull/67253) | Update dependencies |
| 0.0.18 | 2025-09-30 | [66304](https://github.com/airbytehq/airbyte/pull/66304) | Update dependencies |
| 0.0.17 | 2025-09-09 | [66097](https://github.com/airbytehq/airbyte/pull/66097) | Update dependencies |
| 0.0.16 | 2025-08-23 | [65335](https://github.com/airbytehq/airbyte/pull/65335) | Update dependencies |
| 0.0.15 | 2025-08-09 | [64622](https://github.com/airbytehq/airbyte/pull/64622) | Update dependencies |
| 0.0.14 | 2025-08-02 | [64282](https://github.com/airbytehq/airbyte/pull/64282) | Update dependencies |
| 0.0.13 | 2025-07-26 | [63823](https://github.com/airbytehq/airbyte/pull/63823) | Update dependencies |
| 0.0.12 | 2025-07-19 | [63457](https://github.com/airbytehq/airbyte/pull/63457) | Update dependencies |
| 0.0.11 | 2025-07-12 | [63153](https://github.com/airbytehq/airbyte/pull/63153) | Update dependencies |
| 0.0.10 | 2025-07-05 | [62563](https://github.com/airbytehq/airbyte/pull/62563) | Update dependencies |
| 0.0.9 | 2025-06-21 | [61784](https://github.com/airbytehq/airbyte/pull/61784) | Update dependencies |
| 0.0.8 | 2025-06-14 | [61102](https://github.com/airbytehq/airbyte/pull/61102) | Update dependencies |
| 0.0.7 | 2025-05-24 | [60727](https://github.com/airbytehq/airbyte/pull/60727) | Update dependencies |
| 0.0.6 | 2025-05-10 | [59283](https://github.com/airbytehq/airbyte/pull/59283) | Update dependencies |
| 0.0.5 | 2025-04-26 | [58826](https://github.com/airbytehq/airbyte/pull/58826) | Update dependencies |
| 0.0.4 | 2025-04-19 | [58154](https://github.com/airbytehq/airbyte/pull/58154) | Update dependencies |
| 0.0.3 | 2025-04-12 | [57674](https://github.com/airbytehq/airbyte/pull/57674) | Update dependencies |
| 0.0.2 | 2025-04-05 | [57044](https://github.com/airbytehq/airbyte/pull/57044) | Update dependencies |
| 0.0.1 | 2025-04-04 | [57010](https://github.com/airbytehq/airbyte/pull/57010) | Initial release by [@btkcodedev](https://github.com/btkcodedev) via Connector Builder |

</details>

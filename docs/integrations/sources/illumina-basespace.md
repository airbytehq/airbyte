# Illumina Basespace
Connector for the Basespace v1 API. This can be used to extract data on projects, runs, samples and app sessions.

## Configuration

| Input | Type | Description | Default Value |
|-------|------|-------------|---------------|
| `access_token` | `string` | Access Token. BaseSpace access token. Instructions for obtaining your access token can be found in the BaseSpace Developer Documentation. |  |
| `domain` | `string` | Domain. Domain name of the BaseSpace instance (e.g., euw2.sh.basespace.illumina.com) |  |
| `user` | `string` | User. Providing a user ID restricts the returned data to what that user can access. If you use the default (&#39;current&#39;), all data accessible to the user associated with the API key will be shown. | current |

## Streams
| Stream Name | Primary Key | Pagination | Supports Full Sync | Supports Incremental |
|-------------|-------------|------------|---------------------|----------------------|
| projects | Id | DefaultPaginator | ✅ |  ❌  |
| runs | Id | DefaultPaginator | ✅ |  ❌  |
| samples | Id | DefaultPaginator | ✅ |  ❌  |
| sample_files | Id | DefaultPaginator | ✅ |  ❌  |
| run_files | Id | DefaultPaginator | ✅ |  ❌  |
| appsessions | Id | DefaultPaginator | ✅ |  ❌  |
| appresults | Id | DefaultPaginator | ✅ |  ❌  |
| appresults_files | Id | No pagination | ✅ |  ❌  |

## Changelog

<details>
  <summary>Expand to review</summary>

| Version | Date | Pull Request | Subject |
|---------|------|--------------|---------|
| 0.0.44 | 2025-12-09 | [70498](https://github.com/airbytehq/airbyte/pull/70498) | Update dependencies |
| 0.0.43 | 2025-11-25 | [70154](https://github.com/airbytehq/airbyte/pull/70154) | Update dependencies |
| 0.0.42 | 2025-11-18 | [69543](https://github.com/airbytehq/airbyte/pull/69543) | Update dependencies |
| 0.0.41 | 2025-10-29 | [68803](https://github.com/airbytehq/airbyte/pull/68803) | Update dependencies |
| 0.0.40 | 2025-10-21 | [68509](https://github.com/airbytehq/airbyte/pull/68509) | Update dependencies |
| 0.0.39 | 2025-10-14 | [67894](https://github.com/airbytehq/airbyte/pull/67894) | Update dependencies |
| 0.0.38 | 2025-10-07 | [67403](https://github.com/airbytehq/airbyte/pull/67403) | Update dependencies |
| 0.0.37 | 2025-09-30 | [66401](https://github.com/airbytehq/airbyte/pull/66401) | Update dependencies |
| 0.0.36 | 2025-09-09 | [66106](https://github.com/airbytehq/airbyte/pull/66106) | Update dependencies |
| 0.0.35 | 2025-08-23 | [65356](https://github.com/airbytehq/airbyte/pull/65356) | Update dependencies |
| 0.0.34 | 2025-08-09 | [64639](https://github.com/airbytehq/airbyte/pull/64639) | Update dependencies |
| 0.0.33 | 2025-08-02 | [64227](https://github.com/airbytehq/airbyte/pull/64227) | Update dependencies |
| 0.0.32 | 2025-07-26 | [63838](https://github.com/airbytehq/airbyte/pull/63838) | Update dependencies |
| 0.0.31 | 2025-07-19 | [63498](https://github.com/airbytehq/airbyte/pull/63498) | Update dependencies |
| 0.0.30 | 2025-07-12 | [63144](https://github.com/airbytehq/airbyte/pull/63144) | Update dependencies |
| 0.0.29 | 2025-07-05 | [62643](https://github.com/airbytehq/airbyte/pull/62643) | Update dependencies |
| 0.0.28 | 2025-06-28 | [62160](https://github.com/airbytehq/airbyte/pull/62160) | Update dependencies |
| 0.0.27 | 2025-06-21 | [61852](https://github.com/airbytehq/airbyte/pull/61852) | Update dependencies |
| 0.0.26 | 2025-06-14 | [61124](https://github.com/airbytehq/airbyte/pull/61124) | Update dependencies |
| 0.0.25 | 2025-05-24 | [60629](https://github.com/airbytehq/airbyte/pull/60629) | Update dependencies |
| 0.0.24 | 2025-05-10 | [59849](https://github.com/airbytehq/airbyte/pull/59849) | Update dependencies |
| 0.0.23 | 2025-05-03 | [59266](https://github.com/airbytehq/airbyte/pull/59266) | Update dependencies |
| 0.0.22 | 2025-04-26 | [58814](https://github.com/airbytehq/airbyte/pull/58814) | Update dependencies |
| 0.0.21 | 2025-04-19 | [58185](https://github.com/airbytehq/airbyte/pull/58185) | Update dependencies |
| 0.0.20 | 2025-04-12 | [57713](https://github.com/airbytehq/airbyte/pull/57713) | Update dependencies |
| 0.0.19 | 2025-04-05 | [57074](https://github.com/airbytehq/airbyte/pull/57074) | Update dependencies |
| 0.0.18 | 2025-03-29 | [56662](https://github.com/airbytehq/airbyte/pull/56662) | Update dependencies |
| 0.0.17 | 2025-03-22 | [56057](https://github.com/airbytehq/airbyte/pull/56057) | Update dependencies |
| 0.0.16 | 2025-03-08 | [55448](https://github.com/airbytehq/airbyte/pull/55448) | Update dependencies |
| 0.0.15 | 2025-03-01 | [54758](https://github.com/airbytehq/airbyte/pull/54758) | Update dependencies |
| 0.0.14 | 2025-02-22 | [54298](https://github.com/airbytehq/airbyte/pull/54298) | Update dependencies |
| 0.0.13 | 2025-02-15 | [53797](https://github.com/airbytehq/airbyte/pull/53797) | Update dependencies |
| 0.0.12 | 2025-02-08 | [53301](https://github.com/airbytehq/airbyte/pull/53301) | Update dependencies |
| 0.0.11 | 2025-02-01 | [52777](https://github.com/airbytehq/airbyte/pull/52777) | Update dependencies |
| 0.0.10 | 2025-01-25 | [52251](https://github.com/airbytehq/airbyte/pull/52251) | Update dependencies |
| 0.0.9 | 2025-01-18 | [51797](https://github.com/airbytehq/airbyte/pull/51797) | Update dependencies |
| 0.0.8 | 2025-01-11 | [51207](https://github.com/airbytehq/airbyte/pull/51207) | Update dependencies |
| 0.0.7 | 2024-12-28 | [50142](https://github.com/airbytehq/airbyte/pull/50142) | Update dependencies |
| 0.0.6 | 2024-12-14 | [49623](https://github.com/airbytehq/airbyte/pull/49623) | Update dependencies |
| 0.0.5 | 2024-12-12 | [49263](https://github.com/airbytehq/airbyte/pull/49263) | Update dependencies |
| 0.0.4 | 2024-11-04 | [48276](https://github.com/airbytehq/airbyte/pull/48276) | Update dependencies |
| 0.0.3 | 2024-10-29 | [47907](https://github.com/airbytehq/airbyte/pull/47907) | Update dependencies |
| 0.0.2 | 2024-10-28 | [47609](https://github.com/airbytehq/airbyte/pull/47609) | Update dependencies |
| 0.0.1 | 2024-09-23 | | Initial release by [@FilipeJesus](https://github.com/FilipeJesus) via Connector Builder |

</details>

# Google Classroom
Google Classroom connector enables seamless data integration between Google Classroom and various destinations. This connector facilitates the synchronization of course information, rosters, assignments empowering educators to automate reporting and streamline classroom data management efficiently.

## Configuration

| Input | Type | Description | Default Value |
|-------|------|-------------|---------------|
| `client_id` | `string` | OAuth Client ID.  |  |
| `client_secret` | `string` | OAuth Client Secret.  |  |
| `client_refresh_token` | `string` | Refresh token.  |  |

## Streams
| Stream Name | Primary Key | Pagination | Supports Full Sync | Supports Incremental |
|-------------|-------------|------------|---------------------|----------------------|
| courses | id | DefaultPaginator | ✅ |  ❌  |
| teachers | userId | DefaultPaginator | ✅ |  ❌  |
| students | userId | DefaultPaginator | ✅ |  ❌  |
| announcements | id | DefaultPaginator | ✅ |  ❌  |
| coursework | id | DefaultPaginator | ✅ |  ❌  |
| studentsubmissions | id | DefaultPaginator | ✅ |  ❌  |

## Changelog

<details>
  <summary>Expand to review</summary>

| Version          | Date              | Pull Request | Subject        |
|------------------|-------------------|--------------|----------------|
| 0.0.41 | 2025-12-09 | [70700](https://github.com/airbytehq/airbyte/pull/70700) | Update dependencies |
| 0.0.40 | 2025-11-25 | [69900](https://github.com/airbytehq/airbyte/pull/69900) | Update dependencies |
| 0.0.39 | 2025-11-18 | [69413](https://github.com/airbytehq/airbyte/pull/69413) | Update dependencies |
| 0.0.38 | 2025-10-29 | [69026](https://github.com/airbytehq/airbyte/pull/69026) | Update dependencies |
| 0.0.37 | 2025-10-21 | [68327](https://github.com/airbytehq/airbyte/pull/68327) | Update dependencies |
| 0.0.36 | 2025-10-14 | [68003](https://github.com/airbytehq/airbyte/pull/68003) | Update dependencies |
| 0.0.35 | 2025-10-07 | [67265](https://github.com/airbytehq/airbyte/pull/67265) | Update dependencies |
| 0.0.34 | 2025-09-30 | [66301](https://github.com/airbytehq/airbyte/pull/66301) | Update dependencies |
| 0.0.33 | 2025-09-09 | [66067](https://github.com/airbytehq/airbyte/pull/66067) | Update dependencies |
| 0.0.32 | 2025-08-23 | [65313](https://github.com/airbytehq/airbyte/pull/65313) | Update dependencies |
| 0.0.31 | 2025-08-09 | [64590](https://github.com/airbytehq/airbyte/pull/64590) | Update dependencies |
| 0.0.30 | 2025-08-02 | [64198](https://github.com/airbytehq/airbyte/pull/64198) | Update dependencies |
| 0.0.29 | 2025-07-26 | [63833](https://github.com/airbytehq/airbyte/pull/63833) | Update dependencies |
| 0.0.28 | 2025-07-19 | [63530](https://github.com/airbytehq/airbyte/pull/63530) | Update dependencies |
| 0.0.27 | 2025-07-12 | [63136](https://github.com/airbytehq/airbyte/pull/63136) | Update dependencies |
| 0.0.26 | 2025-07-05 | [62587](https://github.com/airbytehq/airbyte/pull/62587) | Update dependencies |
| 0.0.25 | 2025-06-28 | [62199](https://github.com/airbytehq/airbyte/pull/62199) | Update dependencies |
| 0.0.24 | 2025-06-21 | [61853](https://github.com/airbytehq/airbyte/pull/61853) | Update dependencies |
| 0.0.23 | 2025-06-14 | [61143](https://github.com/airbytehq/airbyte/pull/61143) | Update dependencies |
| 0.0.22 | 2025-05-24 | [60701](https://github.com/airbytehq/airbyte/pull/60701) | Update dependencies |
| 0.0.21 | 2025-05-10 | [59252](https://github.com/airbytehq/airbyte/pull/59252) | Update dependencies |
| 0.0.20 | 2025-04-26 | [58766](https://github.com/airbytehq/airbyte/pull/58766) | Update dependencies |
| 0.0.19 | 2025-04-19 | [58196](https://github.com/airbytehq/airbyte/pull/58196) | Update dependencies |
| 0.0.18 | 2025-04-12 | [57673](https://github.com/airbytehq/airbyte/pull/57673) | Update dependencies |
| 0.0.17 | 2025-04-05 | [57080](https://github.com/airbytehq/airbyte/pull/57080) | Update dependencies |
| 0.0.16 | 2025-03-29 | [56534](https://github.com/airbytehq/airbyte/pull/56534) | Update dependencies |
| 0.0.15 | 2025-03-22 | [55922](https://github.com/airbytehq/airbyte/pull/55922) | Update dependencies |
| 0.0.14 | 2025-03-08 | [55336](https://github.com/airbytehq/airbyte/pull/55336) | Update dependencies |
| 0.0.13 | 2025-03-01 | [54985](https://github.com/airbytehq/airbyte/pull/54985) | Update dependencies |
| 0.0.12 | 2025-02-22 | [54442](https://github.com/airbytehq/airbyte/pull/54442) | Update dependencies |
| 0.0.11 | 2025-02-15 | [53786](https://github.com/airbytehq/airbyte/pull/53786) | Update dependencies |
| 0.0.10 | 2025-02-08 | [53349](https://github.com/airbytehq/airbyte/pull/53349) | Update dependencies |
| 0.0.9 | 2025-02-01 | [52818](https://github.com/airbytehq/airbyte/pull/52818) | Update dependencies |
| 0.0.8 | 2025-01-25 | [52366](https://github.com/airbytehq/airbyte/pull/52366) | Update dependencies |
| 0.0.7 | 2025-01-18 | [51669](https://github.com/airbytehq/airbyte/pull/51669) | Update dependencies |
| 0.0.6 | 2025-01-11 | [51128](https://github.com/airbytehq/airbyte/pull/51128) | Update dependencies |
| 0.0.5 | 2024-12-28 | [50545](https://github.com/airbytehq/airbyte/pull/50545) | Update dependencies |
| 0.0.4 | 2024-12-21 | [50010](https://github.com/airbytehq/airbyte/pull/50010) | Update dependencies |
| 0.0.3 | 2024-12-14 | [49540](https://github.com/airbytehq/airbyte/pull/49540) | Update dependencies |
| 0.0.2 | 2024-12-12 | [49188](https://github.com/airbytehq/airbyte/pull/49188) | Update dependencies |
| 0.0.1 | 2024-10-26 | | Initial release by [@bishalbera](https://github.com/bishalbera) via Connector Builder |

</details>

# Onepagecrm
Onepagecrm is a CRM solution for small busineeses.
Using this stream we can extarct data from various streams such as contacts , deals , pipelines and meetings
[API Documentation](https://developer.onepagecrm.com/api/)

## Configuration

| Input | Type | Description | Default Value |
|-------|------|-------------|---------------|
| `username` | `string` | Username. Enter the user ID of your API app |  |
| `password` | `string` | Password. Enter your API Key of your API app |  |

## Streams
| Stream Name | Primary Key | Pagination | Supports Full Sync | Supports Incremental |
|-------------|-------------|------------|---------------------|----------------------|
| contacts | id | DefaultPaginator | ✅ |  ❌  |
| users | id | DefaultPaginator | ✅ |  ❌  |
| bootstrap | user_id | DefaultPaginator | ✅ |  ❌  |
| companies | id | DefaultPaginator | ✅ |  ❌  |
| actions | id | DefaultPaginator | ✅ |  ❌  |
| action_stream |  | DefaultPaginator | ✅ |  ❌  |
| team_stream |  | DefaultPaginator | ✅ |  ❌  |
| deals | id | DefaultPaginator | ✅ |  ❌  |
| notes | id | DefaultPaginator | ✅ |  ❌  |
| relationship_types | id | DefaultPaginator | ✅ |  ❌  |
| pipelines | id | DefaultPaginator | ✅ |  ❌  |
| statuses | id | DefaultPaginator | ✅ |  ❌  |
| lead_sources | id | DefaultPaginator | ✅ |  ❌  |
| filters | id | DefaultPaginator | ✅ |  ❌  |
| predefined_actions | id | DefaultPaginator | ✅ |  ❌  |
| predefined_items | id | DefaultPaginator | ✅ |  ❌  |
| custom_fields | id | DefaultPaginator | ✅ |  ❌  |
| calls | id | DefaultPaginator | ✅ |  ❌  |
| meetings | id | DefaultPaginator | ✅ |  ❌  |

## Changelog

<details>
  <summary>Expand to review</summary>

| Version          | Date              | Pull Request | Subject        |
|------------------|-------------------|--------------|----------------|
| 0.0.43 | 2025-12-09 | [70598](https://github.com/airbytehq/airbyte/pull/70598) | Update dependencies |
| 0.0.42 | 2025-11-25 | [69884](https://github.com/airbytehq/airbyte/pull/69884) | Update dependencies |
| 0.0.41 | 2025-11-18 | [69400](https://github.com/airbytehq/airbyte/pull/69400) | Update dependencies |
| 0.0.40 | 2025-10-29 | [68705](https://github.com/airbytehq/airbyte/pull/68705) | Update dependencies |
| 0.0.39 | 2025-10-21 | [68398](https://github.com/airbytehq/airbyte/pull/68398) | Update dependencies |
| 0.0.38 | 2025-10-14 | [67798](https://github.com/airbytehq/airbyte/pull/67798) | Update dependencies |
| 0.0.37 | 2025-10-07 | [67425](https://github.com/airbytehq/airbyte/pull/67425) | Update dependencies |
| 0.0.36 | 2025-09-30 | [66931](https://github.com/airbytehq/airbyte/pull/66931) | Update dependencies |
| 0.0.35 | 2025-09-23 | [66622](https://github.com/airbytehq/airbyte/pull/66622) | Update dependencies |
| 0.0.34 | 2025-09-09 | [65775](https://github.com/airbytehq/airbyte/pull/65775) | Update dependencies |
| 0.0.33 | 2025-08-23 | [65195](https://github.com/airbytehq/airbyte/pull/65195) | Update dependencies |
| 0.0.32 | 2025-08-09 | [64732](https://github.com/airbytehq/airbyte/pull/64732) | Update dependencies |
| 0.0.31 | 2025-08-02 | [64233](https://github.com/airbytehq/airbyte/pull/64233) | Update dependencies |
| 0.0.30 | 2025-07-26 | [63893](https://github.com/airbytehq/airbyte/pull/63893) | Update dependencies |
| 0.0.29 | 2025-07-19 | [63440](https://github.com/airbytehq/airbyte/pull/63440) | Update dependencies |
| 0.0.28 | 2025-07-12 | [63230](https://github.com/airbytehq/airbyte/pull/63230) | Update dependencies |
| 0.0.27 | 2025-07-05 | [62584](https://github.com/airbytehq/airbyte/pull/62584) | Update dependencies |
| 0.0.26 | 2025-06-28 | [62300](https://github.com/airbytehq/airbyte/pull/62300) | Update dependencies |
| 0.0.25 | 2025-06-21 | [61916](https://github.com/airbytehq/airbyte/pull/61916) | Update dependencies |
| 0.0.24 | 2025-06-14 | [61021](https://github.com/airbytehq/airbyte/pull/61021) | Update dependencies |
| 0.0.23 | 2025-05-24 | [60456](https://github.com/airbytehq/airbyte/pull/60456) | Update dependencies |
| 0.0.22 | 2025-05-10 | [60104](https://github.com/airbytehq/airbyte/pull/60104) | Update dependencies |
| 0.0.21 | 2025-05-03 | [59480](https://github.com/airbytehq/airbyte/pull/59480) | Update dependencies |
| 0.0.20 | 2025-04-27 | [59038](https://github.com/airbytehq/airbyte/pull/59038) | Update dependencies |
| 0.0.19 | 2025-04-19 | [58472](https://github.com/airbytehq/airbyte/pull/58472) | Update dependencies |
| 0.0.18 | 2025-04-12 | [57918](https://github.com/airbytehq/airbyte/pull/57918) | Update dependencies |
| 0.0.17 | 2025-04-05 | [57366](https://github.com/airbytehq/airbyte/pull/57366) | Update dependencies |
| 0.0.16 | 2025-03-29 | [56799](https://github.com/airbytehq/airbyte/pull/56799) | Update dependencies |
| 0.0.15 | 2025-03-22 | [56209](https://github.com/airbytehq/airbyte/pull/56209) | Update dependencies |
| 0.0.14 | 2025-03-08 | [55532](https://github.com/airbytehq/airbyte/pull/55532) | Update dependencies |
| 0.0.13 | 2025-03-01 | [55030](https://github.com/airbytehq/airbyte/pull/55030) | Update dependencies |
| 0.0.12 | 2025-02-23 | [54584](https://github.com/airbytehq/airbyte/pull/54584) | Update dependencies |
| 0.0.11 | 2025-02-15 | [53988](https://github.com/airbytehq/airbyte/pull/53988) | Update dependencies |
| 0.0.10 | 2025-02-08 | [53460](https://github.com/airbytehq/airbyte/pull/53460) | Update dependencies |
| 0.0.9 | 2025-02-01 | [52476](https://github.com/airbytehq/airbyte/pull/52476) | Update dependencies |
| 0.0.8 | 2025-01-18 | [51895](https://github.com/airbytehq/airbyte/pull/51895) | Update dependencies |
| 0.0.7 | 2025-01-11 | [51341](https://github.com/airbytehq/airbyte/pull/51341) | Update dependencies |
| 0.0.6 | 2024-12-28 | [50745](https://github.com/airbytehq/airbyte/pull/50745) | Update dependencies |
| 0.0.5 | 2024-12-21 | [50231](https://github.com/airbytehq/airbyte/pull/50231) | Update dependencies |
| 0.0.4 | 2024-12-14 | [49729](https://github.com/airbytehq/airbyte/pull/49729) | Update dependencies |
| 0.0.3 | 2024-12-12 | [49330](https://github.com/airbytehq/airbyte/pull/49330) | Update dependencies |
| 0.0.2 | 2024-12-11 | [49072](https://github.com/airbytehq/airbyte/pull/49072) | Starting with this version, the Docker image is now rootless. Please note that this and future versions will not be compatible with Airbyte versions earlier than 0.64 |
| 0.0.1 | 2024-11-09 | | Initial release by [@ombhardwajj](https://github.com/ombhardwajj) via Connector Builder |

</details>

# Help Scout
Connector for Help Scout Inbox API 2.0: https://developer.helpscout.com/mailbox-api/
Auth Overview: https://developer.helpscout.com/mailbox-api/overview/authentication/

## Configuration

| Input | Type | Description | Default Value |
|-------|------|-------------|---------------|
| `client_id` | `string` | Application ID.  |  |
| `client_secret` | `string` | Application Secret.  |  |
| `start_date` | `string` | Start date.  |  |

## Streams
| Stream Name | Primary Key | Pagination | Supports Full Sync | Supports Incremental |
|-------------|-------------|------------|---------------------|----------------------|
| conversations | id | DefaultPaginator | ✅ |  ✅  |
| conversation_threads | id | DefaultPaginator | ✅ |  ✅  |
| customers | id | DefaultPaginator | ✅ |  ✅  |
| inboxes | id | DefaultPaginator | ✅ |  ❌  |
| inbox_custom_fields | id | DefaultPaginator | ✅ |  ❌  |
| inbox_folders | id | DefaultPaginator | ✅ |  ❌  |
| users | id | DefaultPaginator | ✅ |  ❌  |
| workflows | id | DefaultPaginator | ✅ |  ❌  |
| tags | id | DefaultPaginator | ✅ |  ❌  |
| teams | id | DefaultPaginator | ✅ |  ❌  |
| team_members | id | DefaultPaginator | ✅ |  ❌  |

## Changelog

<details>
  <summary>Expand to review</summary>

| Version          | Date              | Pull Request                                         | Subject        |
|------------------|-------------------|------------------------------------------------------|----------------|
| 0.0.34 | 2025-12-09 | [70489](https://github.com/airbytehq/airbyte/pull/70489) | Update dependencies |
| 0.0.33 | 2025-11-25 | [70020](https://github.com/airbytehq/airbyte/pull/70020) | Update dependencies |
| 0.0.32 | 2025-11-18 | [69407](https://github.com/airbytehq/airbyte/pull/69407) | Update dependencies |
| 0.0.31 | 2025-10-29 | [68833](https://github.com/airbytehq/airbyte/pull/68833) | Update dependencies |
| 0.0.30 | 2025-10-21 | [68275](https://github.com/airbytehq/airbyte/pull/68275) | Update dependencies |
| 0.0.29 | 2025-10-14 | [67864](https://github.com/airbytehq/airbyte/pull/67864) | Update dependencies |
| 0.0.28 | 2025-10-07 | [67411](https://github.com/airbytehq/airbyte/pull/67411) | Update dependencies |
| 0.0.27 | 2025-09-30 | [66405](https://github.com/airbytehq/airbyte/pull/66405) | Update dependencies |
| 0.0.26 | 2025-09-09 | [66051](https://github.com/airbytehq/airbyte/pull/66051) | Update dependencies |
| 0.0.25 | 2025-08-23 | [65325](https://github.com/airbytehq/airbyte/pull/65325) | Update dependencies |
| 0.0.24 | 2025-08-09 | [64638](https://github.com/airbytehq/airbyte/pull/64638) | Update dependencies |
| 0.0.23 | 2025-08-02 | [64208](https://github.com/airbytehq/airbyte/pull/64208) | Update dependencies |
| 0.0.22 | 2025-07-19 | [63507](https://github.com/airbytehq/airbyte/pull/63507) | Update dependencies |
| 0.0.21 | 2025-07-12 | [63130](https://github.com/airbytehq/airbyte/pull/63130) | Update dependencies |
| 0.0.20 | 2025-07-05 | [62629](https://github.com/airbytehq/airbyte/pull/62629) | Update dependencies |
| 0.0.19 | 2025-06-28 | [62176](https://github.com/airbytehq/airbyte/pull/62176) | Update dependencies |
| 0.0.18 | 2025-06-21 | [61785](https://github.com/airbytehq/airbyte/pull/61785) | Update dependencies |
| 0.0.17 | 2025-06-14 | [61112](https://github.com/airbytehq/airbyte/pull/61112) | Update dependencies |
| 0.0.16 | 2025-05-24 | [60715](https://github.com/airbytehq/airbyte/pull/60715) | Update dependencies |
| 0.0.15 | 2025-05-10 | [59823](https://github.com/airbytehq/airbyte/pull/59823) | Update dependencies |
| 0.0.14 | 2025-05-03 | [59228](https://github.com/airbytehq/airbyte/pull/59228) | Update dependencies |
| 0.0.13 | 2025-04-26 | [58797](https://github.com/airbytehq/airbyte/pull/58797) | Update dependencies |
| 0.0.12 | 2025-04-19 | [58214](https://github.com/airbytehq/airbyte/pull/58214) | Update dependencies |
| 0.0.11 | 2025-04-12 | [57681](https://github.com/airbytehq/airbyte/pull/57681) | Update dependencies |
| 0.0.10 | 2025-04-05 | [57031](https://github.com/airbytehq/airbyte/pull/57031) | Update dependencies |
| 0.0.9 | 2025-03-29 | [56669](https://github.com/airbytehq/airbyte/pull/56669) | Update dependencies |
| 0.0.8 | 2025-03-22 | [56000](https://github.com/airbytehq/airbyte/pull/56000) | Update dependencies |
| 0.0.7 | 2025-03-08 | [55474](https://github.com/airbytehq/airbyte/pull/55474) | Update dependencies |
| 0.0.6 | 2025-03-01 | [54798](https://github.com/airbytehq/airbyte/pull/54798) | Update dependencies |
| 0.0.5 | 2025-02-22 | [54330](https://github.com/airbytehq/airbyte/pull/54330) | Update dependencies |
| 0.0.4 | 2025-02-15 | [53833](https://github.com/airbytehq/airbyte/pull/53833) | Update dependencies |
| 0.0.3 | 2025-02-08 | [53281](https://github.com/airbytehq/airbyte/pull/53281) | Update dependencies |
| 0.0.2 | 2025-02-01 | [52784](https://github.com/airbytehq/airbyte/pull/52784) | Update dependencies |
| 0.0.1 | 2025-01-28 | [52614](https://github.com/airbytehq/airbyte/pull/52614) | Initial release by [@pabloescoder](https://github.com/pabloescoder) via Connector Builder |

</details>

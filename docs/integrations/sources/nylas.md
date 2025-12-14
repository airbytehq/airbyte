# Nylas
The Nylas platform provides an integration layer that makes it easy to connect and sync email, calendar, and contact data from any email service provider.

## Configuration

| Input | Type | Description | Default Value |
|-------|------|-------------|---------------|
| `api_key` | `string` | API Key.  |  |
| `api_server` | `string` | API Server.  |  |
| `start_date` | `string` | Start date.  |  |
| `end_date` | `string` | End date.  |  |

## Streams
| Stream Name | Primary Key | Pagination | Supports Full Sync | Supports Incremental |
|-------------|-------------|------------|---------------------|----------------------|
| calendars | id | DefaultPaginator | ✅ |  ❌  |
| connectors |  | No pagination | ✅ |  ❌  |
| contacts | id | DefaultPaginator | ✅ |  ❌  |
| contact_groups | id | DefaultPaginator | ✅ |  ❌  |
| credentials |  | No pagination | ✅ |  ❌  |
| drafts | id | DefaultPaginator | ✅ |  ✅  |
| events | id | DefaultPaginator | ✅ |  ✅  |
| folders | id | DefaultPaginator | ✅ |  ❌  |
| grants | id | DefaultPaginator | ✅ |  ❌  |
| messages | id | DefaultPaginator | ✅ |  ✅  |
| scheduled_messages | schedule_id | No pagination | ✅ |  ❌  |
| threads | id | DefaultPaginator | ✅ |  ✅  |

## Changelog

<details>
  <summary>Expand to review</summary>

| Version | Date | Pull Request | Subject |
|---------|------|--------------|---------|
| 0.0.45 | 2025-12-09 | [70578](https://github.com/airbytehq/airbyte/pull/70578) | Update dependencies |
| 0.0.44 | 2025-11-25 | [69881](https://github.com/airbytehq/airbyte/pull/69881) | Update dependencies |
| 0.0.43 | 2025-11-18 | [69370](https://github.com/airbytehq/airbyte/pull/69370) | Update dependencies |
| 0.0.42 | 2025-10-29 | [68703](https://github.com/airbytehq/airbyte/pull/68703) | Update dependencies |
| 0.0.41 | 2025-10-21 | [68349](https://github.com/airbytehq/airbyte/pull/68349) | Update dependencies |
| 0.0.40 | 2025-10-14 | [67757](https://github.com/airbytehq/airbyte/pull/67757) | Update dependencies |
| 0.0.39 | 2025-10-07 | [67415](https://github.com/airbytehq/airbyte/pull/67415) | Update dependencies |
| 0.0.38 | 2025-09-30 | [66930](https://github.com/airbytehq/airbyte/pull/66930) | Update dependencies |
| 0.0.37 | 2025-09-23 | [66612](https://github.com/airbytehq/airbyte/pull/66612) | Update dependencies |
| 0.0.36 | 2025-09-09 | [65825](https://github.com/airbytehq/airbyte/pull/65825) | Update dependencies |
| 0.0.35 | 2025-08-23 | [65180](https://github.com/airbytehq/airbyte/pull/65180) | Update dependencies |
| 0.0.34 | 2025-08-09 | [64734](https://github.com/airbytehq/airbyte/pull/64734) | Update dependencies |
| 0.0.33 | 2025-08-02 | [64190](https://github.com/airbytehq/airbyte/pull/64190) | Update dependencies |
| 0.0.32 | 2025-07-26 | [63901](https://github.com/airbytehq/airbyte/pull/63901) | Update dependencies |
| 0.0.31 | 2025-07-19 | [63427](https://github.com/airbytehq/airbyte/pull/63427) | Update dependencies |
| 0.0.30 | 2025-07-12 | [63198](https://github.com/airbytehq/airbyte/pull/63198) | Update dependencies |
| 0.0.29 | 2025-07-05 | [62637](https://github.com/airbytehq/airbyte/pull/62637) | Update dependencies |
| 0.0.28 | 2025-06-28 | [62373](https://github.com/airbytehq/airbyte/pull/62373) | Update dependencies |
| 0.0.27 | 2025-06-21 | [61904](https://github.com/airbytehq/airbyte/pull/61904) | Update dependencies |
| 0.0.26 | 2025-06-14 | [60497](https://github.com/airbytehq/airbyte/pull/60497) | Update dependencies |
| 0.0.25 | 2025-05-10 | [60150](https://github.com/airbytehq/airbyte/pull/60150) | Update dependencies |
| 0.0.24 | 2025-05-03 | [59503](https://github.com/airbytehq/airbyte/pull/59503) | Update dependencies |
| 0.0.23 | 2025-04-27 | [59080](https://github.com/airbytehq/airbyte/pull/59080) | Update dependencies |
| 0.0.22 | 2025-04-19 | [58503](https://github.com/airbytehq/airbyte/pull/58503) | Update dependencies |
| 0.0.21 | 2025-04-12 | [57900](https://github.com/airbytehq/airbyte/pull/57900) | Update dependencies |
| 0.0.20 | 2025-04-05 | [57310](https://github.com/airbytehq/airbyte/pull/57310) | Update dependencies |
| 0.0.19 | 2025-03-29 | [56779](https://github.com/airbytehq/airbyte/pull/56779) | Update dependencies |
| 0.0.18 | 2025-03-22 | [56182](https://github.com/airbytehq/airbyte/pull/56182) | Update dependencies |
| 0.0.17 | 2025-03-08 | [55562](https://github.com/airbytehq/airbyte/pull/55562) | Update dependencies |
| 0.0.16 | 2025-03-01 | [55002](https://github.com/airbytehq/airbyte/pull/55002) | Update dependencies |
| 0.0.15 | 2025-02-23 | [54622](https://github.com/airbytehq/airbyte/pull/54622) | Update dependencies |
| 0.0.14 | 2025-02-15 | [54012](https://github.com/airbytehq/airbyte/pull/54012) | Update dependencies |
| 0.0.13 | 2025-02-08 | [53499](https://github.com/airbytehq/airbyte/pull/53499) | Update dependencies |
| 0.0.12 | 2025-02-01 | [52775](https://github.com/airbytehq/airbyte/pull/52775) | Update dependencies |
| 0.0.11 | 2025-01-25 | [52265](https://github.com/airbytehq/airbyte/pull/52265) | Update dependencies |
| 0.0.10 | 2025-01-18 | [51845](https://github.com/airbytehq/airbyte/pull/51845) | Update dependencies |
| 0.0.9 | 2025-01-11 | [51167](https://github.com/airbytehq/airbyte/pull/51167) | Update dependencies |
| 0.0.8 | 2024-12-28 | [50641](https://github.com/airbytehq/airbyte/pull/50641) | Update dependencies |
| 0.0.7 | 2024-12-21 | [50112](https://github.com/airbytehq/airbyte/pull/50112) | Update dependencies |
| 0.0.6 | 2024-12-14 | [49615](https://github.com/airbytehq/airbyte/pull/49615) | Update dependencies |
| 0.0.5 | 2024-12-12 | [49220](https://github.com/airbytehq/airbyte/pull/49220) | Update dependencies |
| 0.0.4 | 2024-12-11 | [48319](https://github.com/airbytehq/airbyte/pull/48319) | Starting with this version, the Docker image is now rootless. Please note that this and future versions will not be compatible with Airbyte versions earlier than 0.64 |
| 0.0.3 | 2024-10-29 | [47926](https://github.com/airbytehq/airbyte/pull/47926) | Update dependencies |
| 0.0.2 | 2024-10-28 | [47649](https://github.com/airbytehq/airbyte/pull/47649) | Update dependencies |
| 0.0.1 | 2024-09-03 | | Initial release by [@topefolorunso](https://github.com/topefolorunso) via Connector Builder |

</details>

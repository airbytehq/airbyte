# Kissmetrics
This page contains the setup guide and reference information for the [Kissmetrics](https://app.kissmetrics.io/) source connector.

## Documentation reference:
Visit `https://support.kissmetrics.io/reference/overview-1` for API documentation

## Authentication setup
`Kissmetrics` uses Basic Http authentication which uses your username and password,
Refer `https://support.kissmetrics.io/reference/authorization` for more details.

## Configuration

| Input | Type | Description | Default Value |
|-------|------|-------------|---------------|
| `username` | `string` | Username.  |  |
| `password` | `string` | Password.  |  |

## Streams
| Stream Name | Primary Key | Pagination | Supports Full Sync | Supports Incremental |
|-------------|-------------|------------|---------------------|----------------------|
| products | id | DefaultPaginator | ✅ |  ❌  |
| reports | id | DefaultPaginator | ✅ |  ❌  |
| events | id | DefaultPaginator | ✅ |  ❌  |
| properties | id | DefaultPaginator | ✅ |  ❌  |

## Changelog

<details>
  <summary>Expand to review</summary>

| Version | Date | Pull Request | Subject |
|---------| ------------ | --- | ---------------- |
| 0.0.44 | 2025-12-09 | [70751](https://github.com/airbytehq/airbyte/pull/70751) | Update dependencies |
| 0.0.43 | 2025-11-25 | [70049](https://github.com/airbytehq/airbyte/pull/70049) | Update dependencies |
| 0.0.42 | 2025-11-18 | [69478](https://github.com/airbytehq/airbyte/pull/69478) | Update dependencies |
| 0.0.41 | 2025-10-29 | [68766](https://github.com/airbytehq/airbyte/pull/68766) | Update dependencies |
| 0.0.40 | 2025-10-21 | [68318](https://github.com/airbytehq/airbyte/pull/68318) | Update dependencies |
| 0.0.39 | 2025-10-14 | [67956](https://github.com/airbytehq/airbyte/pull/67956) | Update dependencies |
| 0.0.38 | 2025-10-07 | [67372](https://github.com/airbytehq/airbyte/pull/67372) | Update dependencies |
| 0.0.37 | 2025-09-30 | [66808](https://github.com/airbytehq/airbyte/pull/66808) | Update dependencies |
| 0.0.36 | 2025-09-24 | [66644](https://github.com/airbytehq/airbyte/pull/66644) | Update dependencies |
| 0.0.35 | 2025-09-09 | [66047](https://github.com/airbytehq/airbyte/pull/66047) | Update dependencies |
| 0.0.34 | 2025-09-05 | [65966](https://github.com/airbytehq/airbyte/pull/65966) | Update to CDK v7.0.0 |
| 0.0.33 | 2025-08-23 | [65336](https://github.com/airbytehq/airbyte/pull/65336) | Update dependencies |
| 0.0.32 | 2025-08-09 | [64606](https://github.com/airbytehq/airbyte/pull/64606) | Update dependencies |
| 0.0.31 | 2025-08-02 | [64174](https://github.com/airbytehq/airbyte/pull/64174) | Update dependencies |
| 0.0.30 | 2025-07-26 | [63903](https://github.com/airbytehq/airbyte/pull/63903) | Update dependencies |
| 0.0.29 | 2025-07-19 | [63516](https://github.com/airbytehq/airbyte/pull/63516) | Update dependencies |
| 0.0.28 | 2025-07-12 | [63147](https://github.com/airbytehq/airbyte/pull/63147) | Update dependencies |
| 0.0.27 | 2025-07-05 | [62558](https://github.com/airbytehq/airbyte/pull/62558) | Update dependencies |
| 0.0.26 | 2025-06-21 | [61819](https://github.com/airbytehq/airbyte/pull/61819) | Update dependencies |
| 0.0.25 | 2025-06-14 | [61158](https://github.com/airbytehq/airbyte/pull/61158) | Update dependencies |
| 0.0.24 | 2025-05-24 | [60632](https://github.com/airbytehq/airbyte/pull/60632) | Update dependencies |
| 0.0.23 | 2025-05-10 | [59246](https://github.com/airbytehq/airbyte/pull/59246) | Update dependencies |
| 0.0.22 | 2025-04-26 | [58799](https://github.com/airbytehq/airbyte/pull/58799) | Update dependencies |
| 0.0.21 | 2025-04-19 | [57730](https://github.com/airbytehq/airbyte/pull/57730) | Update dependencies |
| 0.0.20 | 2025-04-05 | [57030](https://github.com/airbytehq/airbyte/pull/57030) | Update dependencies |
| 0.0.19 | 2025-03-29 | [56673](https://github.com/airbytehq/airbyte/pull/56673) | Update dependencies |
| 0.0.18 | 2025-03-22 | [56035](https://github.com/airbytehq/airbyte/pull/56035) | Update dependencies |
| 0.0.17 | 2025-03-08 | [55504](https://github.com/airbytehq/airbyte/pull/55504) | Update dependencies |
| 0.0.16 | 2025-03-01 | [54790](https://github.com/airbytehq/airbyte/pull/54790) | Update dependencies |
| 0.0.15 | 2025-02-22 | [54353](https://github.com/airbytehq/airbyte/pull/54353) | Update dependencies |
| 0.0.14 | 2025-02-15 | [53839](https://github.com/airbytehq/airbyte/pull/53839) | Update dependencies |
| 0.0.13 | 2025-02-08 | [53244](https://github.com/airbytehq/airbyte/pull/53244) | Update dependencies |
| 0.0.12 | 2025-02-01 | [52742](https://github.com/airbytehq/airbyte/pull/52742) | Update dependencies |
| 0.0.11 | 2025-01-25 | [52225](https://github.com/airbytehq/airbyte/pull/52225) | Update dependencies |
| 0.0.10 | 2025-01-18 | [51789](https://github.com/airbytehq/airbyte/pull/51789) | Update dependencies |
| 0.0.9 | 2025-01-11 | [51206](https://github.com/airbytehq/airbyte/pull/51206) | Update dependencies |
| 0.0.8 | 2024-12-28 | [50597](https://github.com/airbytehq/airbyte/pull/50597) | Update dependencies |
| 0.0.7 | 2024-12-21 | [50096](https://github.com/airbytehq/airbyte/pull/50096) | Update dependencies |
| 0.0.6 | 2024-12-14 | [49600](https://github.com/airbytehq/airbyte/pull/49600) | Update dependencies |
| 0.0.5 | 2024-12-12 | [49247](https://github.com/airbytehq/airbyte/pull/49247) | Update dependencies |
| 0.0.4 | 2024-11-04 | [48151](https://github.com/airbytehq/airbyte/pull/48151) | Update dependencies |
| 0.0.3 | 2024-10-29 | [47756](https://github.com/airbytehq/airbyte/pull/47756) | Update dependencies |
| 0.0.2 | 2024-10-28 | [47650](https://github.com/airbytehq/airbyte/pull/47650) | Update dependencies |
| 0.0.1 | 2024-09-21 | [45839](https://github.com/airbytehq/airbyte/pull/45839) | Initial release by [@btkcodedev](https://github.com/btkcodedev) via Connector Builder |

</details>

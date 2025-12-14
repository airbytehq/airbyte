# Split-io
This page contains the setup guide and reference information for the [Split-io](https://app.split.io/) source connector.

## Documentation reference:
Visit `https://docs.split.io/reference/introduction` for API documentation

## Authentication setup
Split uses bearer token authentication,
Refer `https://docs.split.io/reference/authentication` for more details.

## Configuration

| Input | Type | Description | Default Value |
|-------|------|-------------|---------------|
| `api_key` | `string` | API Key.  |  |
| `start_date` | `string` | Start date.  |  |

## Streams
| Stream Name | Primary Key | Pagination | Supports Full Sync | Supports Incremental |
|-------------|-------------|------------|---------------------|----------------------|
| changeRequests | id | DefaultPaginator | ✅ |  ❌  |
| workspaces | id | DefaultPaginator | ✅ |  ❌  |
| flagSets | id | DefaultPaginator | ✅ |  ✅  |
| users | id | DefaultPaginator | ✅ |  ❌  |
| segments | name | DefaultPaginator | ✅ |  ✅  |
| segments_keys | uid | DefaultPaginator | ✅ |  ❌  |
| rolloutStatuses | id | DefaultPaginator | ✅ |  ❌  |
| environments | id | DefaultPaginator | ✅ |  ❌  |
| trafficTypes | id | DefaultPaginator | ✅ |  ❌  |
| groups | id | DefaultPaginator | ✅ |  ❌  |
| feature_flags | id | DefaultPaginator | ✅ |  ✅  |

## Changelog

<details>
  <summary>Expand to review</summary>

| Version | Date | Pull Request | Subject |
| ------------------ | ------------ | --- | ---------------- |
| 0.0.39 | 2025-12-09 | [70631](https://github.com/airbytehq/airbyte/pull/70631) | Update dependencies |
| 0.0.38 | 2025-11-25 | [70065](https://github.com/airbytehq/airbyte/pull/70065) | Update dependencies |
| 0.0.37 | 2025-11-18 | [69535](https://github.com/airbytehq/airbyte/pull/69535) | Update dependencies |
| 0.0.36 | 2025-10-29 | [68774](https://github.com/airbytehq/airbyte/pull/68774) | Update dependencies |
| 0.0.35 | 2025-10-21 | [68522](https://github.com/airbytehq/airbyte/pull/68522) | Update dependencies |
| 0.0.34 | 2025-10-14 | [67734](https://github.com/airbytehq/airbyte/pull/67734) | Update dependencies |
| 0.0.33 | 2025-10-07 | [67436](https://github.com/airbytehq/airbyte/pull/67436) | Update dependencies |
| 0.0.32 | 2025-09-30 | [66911](https://github.com/airbytehq/airbyte/pull/66911) | Update dependencies |
| 0.0.31 | 2025-09-24 | [65662](https://github.com/airbytehq/airbyte/pull/65662) | Update dependencies |
| 0.0.30 | 2025-08-23 | [65409](https://github.com/airbytehq/airbyte/pull/65409) | Update dependencies |
| 0.0.29 | 2025-08-16 | [65030](https://github.com/airbytehq/airbyte/pull/65030) | Update dependencies |
| 0.0.28 | 2025-08-02 | [64428](https://github.com/airbytehq/airbyte/pull/64428) | Update dependencies |
| 0.0.27 | 2025-07-26 | [63974](https://github.com/airbytehq/airbyte/pull/63974) | Update dependencies |
| 0.0.26 | 2025-07-12 | [63049](https://github.com/airbytehq/airbyte/pull/63049) | Update dependencies |
| 0.0.25 | 2025-07-05 | [62667](https://github.com/airbytehq/airbyte/pull/62667) | Update dependencies |
| 0.0.24 | 2025-06-28 | [61468](https://github.com/airbytehq/airbyte/pull/61468) | Update dependencies |
| 0.0.23 | 2025-05-25 | [60583](https://github.com/airbytehq/airbyte/pull/60583) | Update dependencies |
| 0.0.22 | 2025-05-10 | [60064](https://github.com/airbytehq/airbyte/pull/60064) | Update dependencies |
| 0.0.21 | 2025-05-04 | [59618](https://github.com/airbytehq/airbyte/pull/59618) | Update dependencies |
| 0.0.20 | 2025-04-27 | [59024](https://github.com/airbytehq/airbyte/pull/59024) | Update dependencies |
| 0.0.19 | 2025-04-19 | [58407](https://github.com/airbytehq/airbyte/pull/58407) | Update dependencies |
| 0.0.18 | 2025-04-12 | [57992](https://github.com/airbytehq/airbyte/pull/57992) | Update dependencies |
| 0.0.17 | 2025-04-05 | [57469](https://github.com/airbytehq/airbyte/pull/57469) | Update dependencies |
| 0.0.16 | 2025-03-29 | [56844](https://github.com/airbytehq/airbyte/pull/56844) | Update dependencies |
| 0.0.15 | 2025-03-22 | [56306](https://github.com/airbytehq/airbyte/pull/56306) | Update dependencies |
| 0.0.14 | 2025-03-08 | [55602](https://github.com/airbytehq/airbyte/pull/55602) | Update dependencies |
| 0.0.13 | 2025-03-01 | [55078](https://github.com/airbytehq/airbyte/pull/55078) | Update dependencies |
| 0.0.12 | 2025-02-22 | [54470](https://github.com/airbytehq/airbyte/pull/54470) | Update dependencies |
| 0.0.11 | 2025-02-15 | [54064](https://github.com/airbytehq/airbyte/pull/54064) | Update dependencies |
| 0.0.10 | 2025-02-08 | [53536](https://github.com/airbytehq/airbyte/pull/53536) | Update dependencies |
| 0.0.9 | 2025-02-01 | [53053](https://github.com/airbytehq/airbyte/pull/53053) | Update dependencies |
| 0.0.8 | 2025-01-25 | [52419](https://github.com/airbytehq/airbyte/pull/52419) | Update dependencies |
| 0.0.7 | 2025-01-18 | [51980](https://github.com/airbytehq/airbyte/pull/51980) | Update dependencies |
| 0.0.6 | 2025-01-11 | [51425](https://github.com/airbytehq/airbyte/pull/51425) | Update dependencies |
| 0.0.5 | 2024-12-28 | [50791](https://github.com/airbytehq/airbyte/pull/50791) | Update dependencies |
| 0.0.4 | 2024-12-21 | [50320](https://github.com/airbytehq/airbyte/pull/50320) | Update dependencies |
| 0.0.3 | 2024-12-14 | [49735](https://github.com/airbytehq/airbyte/pull/49735) | Update dependencies |
| 0.0.2 | 2024-12-12 | [49402](https://github.com/airbytehq/airbyte/pull/49402) | Update dependencies |
| 0.0.1 | 2024-09-18 | [45367](https://github.com/airbytehq/airbyte/pull/45367) | Initial release by [@btkcodedev](https://github.com/btkcodedev) via Connector Builder |

</details>

# Missive
This page contains the setup guide and reference information for the [Missive](https://missiveapp.com/) source connector.

## Documentation reference:
Visit `https://missiveapp.com/help/api-documentation/rest-endpoints` for API documentation

## Authentication setup
`Missive` uses Bearer token authentication authentication, Visit your profile settings for getting your api keys. Refer `https://missiveapp.com/help/api-documentation/getting-started` for more details.

## Configuration

| Input | Type | Description | Default Value |
|-------|------|-------------|---------------|
| `api_key` | `string` | API Key.  |  |
| `limit` | `string` | Limit. Max records per page limit | 50 |
| `start_date` | `string` | Start date.  |  |
| `kind` | `string` | Kind. Kind parameter for `contact_groups` stream | group |

## Streams
| Stream Name | Primary Key | Pagination | Supports Full Sync | Supports Incremental |
|-------------|-------------|------------|---------------------|----------------------|
| contact_books | id | DefaultPaginator | ✅ |  ❌  |
| contacts | id | DefaultPaginator | ✅ |  ✅  |
| contact_groups | id | DefaultPaginator | ✅ |  ❌  |
| users | id | DefaultPaginator | ✅ |  ❌  |
| teams | id | DefaultPaginator | ✅ |  ❌  |
| shared_labels | id | DefaultPaginator | ✅ |  ❌  |
| organizations | id | DefaultPaginator | ✅ |  ❌  |
| conversations | id | No pagination | ✅ |  ✅  |

## Changelog

<details>
  <summary>Expand to review</summary>

| Version | Date | Pull Request | Subject |
| ------------------ | ------------ | --- | ---------------- |
| 0.0.41 | 2025-12-09 | [70746](https://github.com/airbytehq/airbyte/pull/70746) | Update dependencies |
| 0.0.40 | 2025-11-25 | [70129](https://github.com/airbytehq/airbyte/pull/70129) | Update dependencies |
| 0.0.39 | 2025-11-18 | [69582](https://github.com/airbytehq/airbyte/pull/69582) | Update dependencies |
| 0.0.38 | 2025-10-29 | [69051](https://github.com/airbytehq/airbyte/pull/69051) | Update dependencies |
| 0.0.37 | 2025-10-21 | [68447](https://github.com/airbytehq/airbyte/pull/68447) | Update dependencies |
| 0.0.36 | 2025-10-14 | [67818](https://github.com/airbytehq/airbyte/pull/67818) | Update dependencies |
| 0.0.35 | 2025-10-07 | [67381](https://github.com/airbytehq/airbyte/pull/67381) | Update dependencies |
| 0.0.34 | 2025-09-30 | [66345](https://github.com/airbytehq/airbyte/pull/66345) | Update dependencies |
| 0.0.33 | 2025-09-09 | [65817](https://github.com/airbytehq/airbyte/pull/65817) | Update dependencies |
| 0.0.32 | 2025-08-23 | [65204](https://github.com/airbytehq/airbyte/pull/65204) | Update dependencies |
| 0.0.31 | 2025-08-09 | [64723](https://github.com/airbytehq/airbyte/pull/64723) | Update dependencies |
| 0.0.30 | 2025-08-02 | [64196](https://github.com/airbytehq/airbyte/pull/64196) | Update dependencies |
| 0.0.29 | 2025-07-26 | [63814](https://github.com/airbytehq/airbyte/pull/63814) | Update dependencies |
| 0.0.28 | 2025-07-19 | [63423](https://github.com/airbytehq/airbyte/pull/63423) | Update dependencies |
| 0.0.27 | 2025-07-12 | [63267](https://github.com/airbytehq/airbyte/pull/63267) | Update dependencies |
| 0.0.26 | 2025-07-05 | [62608](https://github.com/airbytehq/airbyte/pull/62608) | Update dependencies |
| 0.0.25 | 2025-06-28 | [62333](https://github.com/airbytehq/airbyte/pull/62333) | Update dependencies |
| 0.0.24 | 2025-06-21 | [61921](https://github.com/airbytehq/airbyte/pull/61921) | Update dependencies |
| 0.0.23 | 2025-06-14 | [61038](https://github.com/airbytehq/airbyte/pull/61038) | Update dependencies |
| 0.0.22 | 2025-05-24 | [60202](https://github.com/airbytehq/airbyte/pull/60202) | Update dependencies |
| 0.0.21 | 2025-05-03 | [59460](https://github.com/airbytehq/airbyte/pull/59460) | Update dependencies |
| 0.0.20 | 2025-04-27 | [59098](https://github.com/airbytehq/airbyte/pull/59098) | Update dependencies |
| 0.0.19 | 2025-04-19 | [57913](https://github.com/airbytehq/airbyte/pull/57913) | Update dependencies |
| 0.0.18 | 2025-04-05 | [57048](https://github.com/airbytehq/airbyte/pull/57048) | Update dependencies |
| 0.0.17 | 2025-03-29 | [56709](https://github.com/airbytehq/airbyte/pull/56709) | Update dependencies |
| 0.0.16 | 2025-03-22 | [56070](https://github.com/airbytehq/airbyte/pull/56070) | Update dependencies |
| 0.0.15 | 2025-03-08 | [55478](https://github.com/airbytehq/airbyte/pull/55478) | Update dependencies |
| 0.0.14 | 2025-03-01 | [54823](https://github.com/airbytehq/airbyte/pull/54823) | Update dependencies |
| 0.0.13 | 2025-02-22 | [54289](https://github.com/airbytehq/airbyte/pull/54289) | Update dependencies |
| 0.0.12 | 2025-02-15 | [53831](https://github.com/airbytehq/airbyte/pull/53831) | Update dependencies |
| 0.0.11 | 2025-02-08 | [53297](https://github.com/airbytehq/airbyte/pull/53297) | Update dependencies |
| 0.0.10 | 2025-02-01 | [52785](https://github.com/airbytehq/airbyte/pull/52785) | Update dependencies |
| 0.0.9 | 2025-01-25 | [52289](https://github.com/airbytehq/airbyte/pull/52289) | Update dependencies |
| 0.0.8 | 2025-01-18 | [51808](https://github.com/airbytehq/airbyte/pull/51808) | Update dependencies |
| 0.0.7 | 2025-01-11 | [51183](https://github.com/airbytehq/airbyte/pull/51183) | Update dependencies |
| 0.0.6 | 2024-12-28 | [50141](https://github.com/airbytehq/airbyte/pull/50141) | Update dependencies |
| 0.0.5 | 2024-12-14 | [49631](https://github.com/airbytehq/airbyte/pull/49631) | Update dependencies |
| 0.0.4 | 2024-12-12 | [49238](https://github.com/airbytehq/airbyte/pull/49238) | Update dependencies |
| 0.0.3 | 2024-12-11 | [47796](https://github.com/airbytehq/airbyte/pull/47796) | Starting with this version, the Docker image is now rootless. Please note that this and future versions will not be compatible with Airbyte versions earlier than 0.64 |
| 0.0.2 | 2024-10-28 | [47599](https://github.com/airbytehq/airbyte/pull/47599) | Update dependencies |
| 0.0.1 | 2024-09-22 | [45844](https://github.com/airbytehq/airbyte/pull/45844) | Initial release by [@btkcodedev](https://github.com/btkcodedev) via Connector Builder |

</details>

# When_i_work
This page contains the setup guide and reference information for the [When I Work](https://wheniwork.com/) source connector.

## Documentation reference:
Visit `https://apidocs.wheniwork.com/external/index.html` for API documentation

## Authentication setup
`When I work` uses session token authentication,
You have to give your login email and password used with `when-i-work` account for authentication.
`https://apidocs.wheniwork.com/external/index.html?repo=login`

## Configuration

| Input | Type | Description | Default Value |
|-------|------|-------------|---------------|
| `api_key` | `string` | API Key.  |  |

## Streams
| Stream Name | Primary Key | Pagination | Supports Full Sync | Supports Incremental |
|-------------|-------------|------------|---------------------|----------------------|
| account | id | DefaultPaginator | ✅ |  ❌  |
| payrolls | id | DefaultPaginator | ✅ |  ❌  |
| users | id | DefaultPaginator | ✅ |  ❌  |
| timezones | id | No pagination | ✅ |  ❌  |
| payrolls_notices | uid | No pagination | ✅ |  ❌  |
| times | uid | No pagination | ✅ |  ❌  |
| requests | id | DefaultPaginator | ✅ |  ❌  |
| blocks | id | DefaultPaginator | ✅ |  ❌  |
| sites | id | DefaultPaginator | ✅ |  ❌  |
| locations | id | DefaultPaginator | ✅ |  ❌  |
| positions | id | No pagination | ✅ |  ❌  |
| openshiftapprovalrequests | uid | DefaultPaginator | ✅ |  ❌  |

## Changelog

<details>
  <summary>Expand to review</summary>

| Version | Date | Pull Request | Subject |
| ------------------ | ------------ | --- | ---------------- |
| 0.0.43 | 2025-12-09 | [70692](https://github.com/airbytehq/airbyte/pull/70692) | Update dependencies |
| 0.0.42 | 2025-11-25 | [70171](https://github.com/airbytehq/airbyte/pull/70171) | Update dependencies |
| 0.0.41 | 2025-11-18 | [69697](https://github.com/airbytehq/airbyte/pull/69697) | Update dependencies |
| 0.0.40 | 2025-10-29 | [68955](https://github.com/airbytehq/airbyte/pull/68955) | Update dependencies |
| 0.0.39 | 2025-10-21 | [68394](https://github.com/airbytehq/airbyte/pull/68394) | Update dependencies |
| 0.0.38 | 2025-10-14 | [67971](https://github.com/airbytehq/airbyte/pull/67971) | Update dependencies |
| 0.0.37 | 2025-10-07 | [67321](https://github.com/airbytehq/airbyte/pull/67321) | Update dependencies |
| 0.0.36 | 2025-09-30 | [66450](https://github.com/airbytehq/airbyte/pull/66450) | Update dependencies |
| 0.0.35 | 2025-09-09 | [65692](https://github.com/airbytehq/airbyte/pull/65692) | Update dependencies |
| 0.0.34 | 2025-08-24 | [65481](https://github.com/airbytehq/airbyte/pull/65481) | Update dependencies |
| 0.0.33 | 2025-08-09 | [64803](https://github.com/airbytehq/airbyte/pull/64803) | Update dependencies |
| 0.0.32 | 2025-08-02 | [64306](https://github.com/airbytehq/airbyte/pull/64306) | Update dependencies |
| 0.0.31 | 2025-07-26 | [64058](https://github.com/airbytehq/airbyte/pull/64058) | Update dependencies |
| 0.0.30 | 2025-07-20 | [63684](https://github.com/airbytehq/airbyte/pull/63684) | Update dependencies |
| 0.0.29 | 2025-07-12 | [63179](https://github.com/airbytehq/airbyte/pull/63179) | Update dependencies |
| 0.0.28 | 2025-07-05 | [62700](https://github.com/airbytehq/airbyte/pull/62700) | Update dependencies |
| 0.0.27 | 2025-06-28 | [62261](https://github.com/airbytehq/airbyte/pull/62261) | Update dependencies |
| 0.0.26 | 2025-06-21 | [61769](https://github.com/airbytehq/airbyte/pull/61769) | Update dependencies |
| 0.0.25 | 2025-06-15 | [61194](https://github.com/airbytehq/airbyte/pull/61194) | Update dependencies |
| 0.0.24 | 2025-05-24 | [60772](https://github.com/airbytehq/airbyte/pull/60772) | Update dependencies |
| 0.0.23 | 2025-05-10 | [59976](https://github.com/airbytehq/airbyte/pull/59976) | Update dependencies |
| 0.0.22 | 2025-05-04 | [59560](https://github.com/airbytehq/airbyte/pull/59560) | Update dependencies |
| 0.0.21 | 2025-04-26 | [58934](https://github.com/airbytehq/airbyte/pull/58934) | Update dependencies |
| 0.0.20 | 2025-04-19 | [58535](https://github.com/airbytehq/airbyte/pull/58535) | Update dependencies |
| 0.0.19 | 2025-04-13 | [58057](https://github.com/airbytehq/airbyte/pull/58057) | Update dependencies |
| 0.0.18 | 2025-04-05 | [57400](https://github.com/airbytehq/airbyte/pull/57400) | Update dependencies |
| 0.0.17 | 2025-03-29 | [56807](https://github.com/airbytehq/airbyte/pull/56807) | Update dependencies |
| 0.0.16 | 2025-03-22 | [56249](https://github.com/airbytehq/airbyte/pull/56249) | Update dependencies |
| 0.0.15 | 2025-03-09 | [55650](https://github.com/airbytehq/airbyte/pull/55650) | Update dependencies |
| 0.0.14 | 2025-03-01 | [55123](https://github.com/airbytehq/airbyte/pull/55123) | Update dependencies |
| 0.0.13 | 2025-02-22 | [54473](https://github.com/airbytehq/airbyte/pull/54473) | Update dependencies |
| 0.0.12 | 2025-02-15 | [54045](https://github.com/airbytehq/airbyte/pull/54045) | Update dependencies |
| 0.0.11 | 2025-02-08 | [53540](https://github.com/airbytehq/airbyte/pull/53540) | Update dependencies |
| 0.0.10 | 2025-02-01 | [52440](https://github.com/airbytehq/airbyte/pull/52440) | Update dependencies |
| 0.0.9 | 2025-01-18 | [51985](https://github.com/airbytehq/airbyte/pull/51985) | Update dependencies |
| 0.0.8 | 2025-01-11 | [51415](https://github.com/airbytehq/airbyte/pull/51415) | Update dependencies |
| 0.0.7 | 2024-12-28 | [50771](https://github.com/airbytehq/airbyte/pull/50771) | Update dependencies |
| 0.0.6 | 2024-12-21 | [50374](https://github.com/airbytehq/airbyte/pull/50374) | Update dependencies |
| 0.0.5 | 2024-12-14 | [49795](https://github.com/airbytehq/airbyte/pull/49795) | Update dependencies |
| 0.0.4 | 2024-12-12 | [49389](https://github.com/airbytehq/airbyte/pull/49389) | Update dependencies |
| 0.0.3 | 2024-11-04 | [48303](https://github.com/airbytehq/airbyte/pull/48303) | Update dependencies |
| 0.0.2 | 2024-10-28 | [47565](https://github.com/airbytehq/airbyte/pull/47565) | Update dependencies |
| 0.0.1 | 2024-09-10 | [45367](https://github.com/airbytehq/airbyte/pull/45367) | Initial release by [@btkcodedev](https://github.com/btkcodedev) via Connector Builder |

</details>

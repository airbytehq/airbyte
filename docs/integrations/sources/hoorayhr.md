# HoorayHR

Source connector for HoorayHR (https://hoorayhr.io). The connector uses https://api.hoorayhr.io

## Configuration

Use the credentials of your HoorayHR account to configure the connector. Make sure MFA is disabled. Currently this is a limitation of the HoorayHR API.

| Input              | Type     | Description        | Default Value |
| ------------------ | -------- | ------------------ | ------------- |
| `hoorayhrusername` | `string` | HoorayHR Username. |               |
| `hoorayhrpassword` | `string` | HoorayHR Password. |               |

## Streams

| Stream Name | Primary Key | Pagination    | Supports Full Sync | Supports Incremental |
| ----------- | ----------- | ------------- | ------------------ | -------------------- |
| sick-leaves | id          | No pagination | ✅                 | ❌                   |
| time-off    | id          | No pagination | ✅                 | ❌                   |
| leave-types | id          | No pagination | ✅                 | ❌                   |
| users       | id          | No pagination | ✅                 | ❌                   |

## Changelog

<details>
  <summary>Expand to review</summary>

| Version | Date       | Pull Request | Subject                                                                                             |
| ------- | ---------- | ------------ | --------------------------------------------------------------------------------------------------- |
| 0.1.16 | 2025-04-19 | [58169](https://github.com/airbytehq/airbyte/pull/58169) | Update dependencies |
| 0.1.15 | 2025-04-12 | [57735](https://github.com/airbytehq/airbyte/pull/57735) | Update dependencies |
| 0.1.14 | 2025-04-05 | [57070](https://github.com/airbytehq/airbyte/pull/57070) | Update dependencies |
| 0.1.13 | 2025-03-29 | [56652](https://github.com/airbytehq/airbyte/pull/56652) | Update dependencies |
| 0.1.12 | 2025-03-22 | [56047](https://github.com/airbytehq/airbyte/pull/56047) | Update dependencies |
| 0.1.11 | 2025-03-08 | [55439](https://github.com/airbytehq/airbyte/pull/55439) | Update dependencies |
| 0.1.10 | 2025-03-01 | [54756](https://github.com/airbytehq/airbyte/pull/54756) | Update dependencies |
| 0.1.9 | 2025-02-22 | [54350](https://github.com/airbytehq/airbyte/pull/54350) | Update dependencies |
| 0.1.8 | 2025-02-15 | [53840](https://github.com/airbytehq/airbyte/pull/53840) | Update dependencies |
| 0.1.7 | 2025-02-08 | [53294](https://github.com/airbytehq/airbyte/pull/53294) | Update dependencies |
| 0.1.6 | 2025-02-01 | [52762](https://github.com/airbytehq/airbyte/pull/52762) | Update dependencies |
| 0.1.5 | 2025-01-25 | [52250](https://github.com/airbytehq/airbyte/pull/52250) | Update dependencies |
| 0.1.4 | 2025-01-18 | [51784](https://github.com/airbytehq/airbyte/pull/51784) | Update dependencies |
| 0.1.3 | 2025-01-11 | [51151](https://github.com/airbytehq/airbyte/pull/51151) | Update dependencies |
| 0.1.2 | 2024-12-28 | [50598](https://github.com/airbytehq/airbyte/pull/50598) | Update dependencies |
| 0.1.1 | 2024-12-21 | [50110](https://github.com/airbytehq/airbyte/pull/50110) | Update dependencies |
| 0.1.0   | 2024-12-17 |              | Added some more documentation and icon for HoorayHR by [@JoeriSmits](https://github.com/JoeriSmits) |
| 0.0.1   | 2024-12-17 |              | Initial release by [@JoeriSmits](https://github.com/JoeriSmits) via Connector Builder               |

</details>

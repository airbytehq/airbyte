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
| 0.1.2 | 2024-12-28 | [50598](https://github.com/airbytehq/airbyte/pull/50598) | Update dependencies |
| 0.1.1 | 2024-12-21 | [50110](https://github.com/airbytehq/airbyte/pull/50110) | Update dependencies |
| 0.1.0   | 2024-12-17 |              | Added some more documentation and icon for HoorayHR by [@JoeriSmits](https://github.com/JoeriSmits) |
| 0.0.1   | 2024-12-17 |              | Initial release by [@JoeriSmits](https://github.com/JoeriSmits) via Connector Builder               |

</details>

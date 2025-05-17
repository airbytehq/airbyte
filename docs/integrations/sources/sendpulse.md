# SendPulse
Airbyte connector for [SendPulse](https://sendpulse.com/) allows you to seamlessly sync data from SendPulse to your data warehouse. It retrieves essential information from various SendPulse streams, including mailing lists, campaigns, templates, senders, webhooks, balance details, and balance. This enables you to analyze and manage your SendPulse email marketing and communication efforts effectively in a centralized location.

## Configuration

| Input | Type | Description | Default Value |
|-------|------|-------------|---------------|
| `client_id` | `string` | OAuth Client ID.  |  |
| `client_secret` | `string` | OAuth Client Secret.  |  |

## Streams
| Stream Name | Primary Key | Pagination | Supports Full Sync | Supports Incremental |
|-------------|-------------|------------|---------------------|----------------------|
| mailing_lists | id | DefaultPaginator | ✅ |  ❌  |
| campaigns | id | DefaultPaginator | ✅ |  ❌  |
| templates | id | No pagination | ✅ |  ❌  |
| senders | email | No pagination | ✅ |  ❌  |
| webhooks | id | No pagination | ✅ |  ❌  |
| balance_details |  | No pagination | ✅ |  ❌  |
| balance | currency | No pagination | ✅ |  ❌  |

## Changelog

<details>
  <summary>Expand to review</summary>

| Version          | Date              | Pull Request | Subject        |
|------------------|-------------------|--------------|----------------|
| 0.0.23 | 2025-05-17 | [60574](https://github.com/airbytehq/airbyte/pull/60574) | Update dependencies |
| 0.0.22 | 2025-05-10 | [60200](https://github.com/airbytehq/airbyte/pull/60200) | Update dependencies |
| 0.0.21 | 2025-05-04 | [59626](https://github.com/airbytehq/airbyte/pull/59626) | Update dependencies |
| 0.0.20 | 2025-04-27 | [59009](https://github.com/airbytehq/airbyte/pull/59009) | Update dependencies |
| 0.0.19 | 2025-04-19 | [58389](https://github.com/airbytehq/airbyte/pull/58389) | Update dependencies |
| 0.0.18 | 2025-04-12 | [57977](https://github.com/airbytehq/airbyte/pull/57977) | Update dependencies |
| 0.0.17 | 2025-04-05 | [57459](https://github.com/airbytehq/airbyte/pull/57459) | Update dependencies |
| 0.0.16 | 2025-03-29 | [56866](https://github.com/airbytehq/airbyte/pull/56866) | Update dependencies |
| 0.0.15 | 2025-03-22 | [56305](https://github.com/airbytehq/airbyte/pull/56305) | Update dependencies |
| 0.0.14 | 2025-03-08 | [55539](https://github.com/airbytehq/airbyte/pull/55539) | Update dependencies |
| 0.0.13 | 2025-03-01 | [54574](https://github.com/airbytehq/airbyte/pull/54574) | Update dependencies |
| 0.0.12 | 2025-02-15 | [53951](https://github.com/airbytehq/airbyte/pull/53951) | Update dependencies |
| 0.0.11 | 2025-02-08 | [53505](https://github.com/airbytehq/airbyte/pull/53505) | Update dependencies |
| 0.0.10 | 2025-02-01 | [52959](https://github.com/airbytehq/airbyte/pull/52959) | Update dependencies |
| 0.0.9 | 2025-01-25 | [52528](https://github.com/airbytehq/airbyte/pull/52528) | Update dependencies |
| 0.0.8 | 2025-01-18 | [51905](https://github.com/airbytehq/airbyte/pull/51905) | Update dependencies |
| 0.0.7 | 2025-01-11 | [51310](https://github.com/airbytehq/airbyte/pull/51310) | Update dependencies |
| 0.0.6 | 2024-12-28 | [50700](https://github.com/airbytehq/airbyte/pull/50700) | Update dependencies |
| 0.0.5 | 2024-12-21 | [50259](https://github.com/airbytehq/airbyte/pull/50259) | Update dependencies |
| 0.0.4 | 2024-12-14 | [49677](https://github.com/airbytehq/airbyte/pull/49677) | Update dependencies |
| 0.0.3 | 2024-12-12 | [49323](https://github.com/airbytehq/airbyte/pull/49323) | Update dependencies |
| 0.0.2 | 2024-12-11 | [49061](https://github.com/airbytehq/airbyte/pull/49061) | Starting with this version, the Docker image is now rootless. Please note that this and future versions will not be compatible with Airbyte versions earlier than 0.64 |
| 0.0.1 | 2024-11-08 | | Initial release by [@parthiv11](https://github.com/parthiv11) via Connector Builder |

</details>

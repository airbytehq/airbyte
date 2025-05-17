# Mailtrap

Email Delivery Platform for individuals and businesses to test, send and control email infrastructure in one place.

[API Documentation](https://api-docs.mailtrap.io/docs/mailtrap-api-docs/5tjdeg9545058-mailtrap-api)

## Configuration

| Input | Type | Description | Default Value |
|-------|------|-------------|---------------|
| `api_token` | `string` | API Token. API token to use. Find it at https://mailtrap.io/account |  |

## Streams
| Stream Name | Primary Key | Pagination | Supports Full Sync | Supports Incremental |
|-------------|-------------|------------|---------------------|----------------------|
| accounts | id | No pagination | ✅ |  ❌  |
| billing_usage | uuid | No pagination | ✅ |  ❌  |
| resources | id | No pagination | ✅ |  ❌  |
| sending_domains | id | No pagination | ✅ |  ❌  |
| inboxes | id | No pagination | ✅ |  ❌  |
| messages | id | No pagination | ✅ |  ❌  |
| projects | id | No pagination | ✅ |  ❌  |

## Changelog

<details>
  <summary>Expand to review</summary>

| Version          | Date              | Pull Request | Subject        |
|------------------|-------------------|--------------|----------------|
| 0.0.23 | 2025-05-17 | [60616](https://github.com/airbytehq/airbyte/pull/60616) | Update dependencies |
| 0.0.22 | 2025-05-10 | [59822](https://github.com/airbytehq/airbyte/pull/59822) | Update dependencies |
| 0.0.21 | 2025-05-03 | [59238](https://github.com/airbytehq/airbyte/pull/59238) | Update dependencies |
| 0.0.20 | 2025-04-26 | [58177](https://github.com/airbytehq/airbyte/pull/58177) | Update dependencies |
| 0.0.19 | 2025-04-12 | [57697](https://github.com/airbytehq/airbyte/pull/57697) | Update dependencies |
| 0.0.18 | 2025-04-05 | [57095](https://github.com/airbytehq/airbyte/pull/57095) | Update dependencies |
| 0.0.17 | 2025-03-29 | [56689](https://github.com/airbytehq/airbyte/pull/56689) | Update dependencies |
| 0.0.16 | 2025-03-22 | [56064](https://github.com/airbytehq/airbyte/pull/56064) | Update dependencies |
| 0.0.15 | 2025-03-08 | [55438](https://github.com/airbytehq/airbyte/pull/55438) | Update dependencies |
| 0.0.14 | 2025-03-01 | [54799](https://github.com/airbytehq/airbyte/pull/54799) | Update dependencies |
| 0.0.13 | 2025-02-22 | [54354](https://github.com/airbytehq/airbyte/pull/54354) | Update dependencies |
| 0.0.12 | 2025-02-15 | [53801](https://github.com/airbytehq/airbyte/pull/53801) | Update dependencies |
| 0.0.11 | 2025-02-08 | [53298](https://github.com/airbytehq/airbyte/pull/53298) | Update dependencies |
| 0.0.10 | 2025-02-01 | [52713](https://github.com/airbytehq/airbyte/pull/52713) | Update dependencies |
| 0.0.9 | 2025-01-25 | [52259](https://github.com/airbytehq/airbyte/pull/52259) | Update dependencies |
| 0.0.8 | 2025-01-18 | [51847](https://github.com/airbytehq/airbyte/pull/51847) | Update dependencies |
| 0.0.7 | 2025-01-11 | [51145](https://github.com/airbytehq/airbyte/pull/51145) | Update dependencies |
| 0.0.6 | 2024-12-28 | [50593](https://github.com/airbytehq/airbyte/pull/50593) | Update dependencies |
| 0.0.5 | 2024-12-21 | [50143](https://github.com/airbytehq/airbyte/pull/50143) | Update dependencies |
| 0.0.4 | 2024-12-14 | [49649](https://github.com/airbytehq/airbyte/pull/49649) | Update dependencies |
| 0.0.3 | 2024-12-12 | [49256](https://github.com/airbytehq/airbyte/pull/49256) | Update dependencies |
| 0.0.2 | 2024-12-11 | [48968](https://github.com/airbytehq/airbyte/pull/48968) | Starting with this version, the Docker image is now rootless. Please note that this and future versions will not be compatible with Airbyte versions earlier than 0.64 |
| 0.0.1 | 2024-10-23 | | Initial release by [@gemsteam](https://github.com/gemsteam) via Connector Builder |

</details>

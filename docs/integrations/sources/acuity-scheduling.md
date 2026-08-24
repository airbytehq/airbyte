# Acuity Scheduling
Flexible scheduling software to help you succeed
With seamless client scheduling, secure payments, and workflow automation, all you have to do is show up on time.

## Configuration

| Input | Type | Description | Default Value |
|-------|------|-------------|---------------|
| `username` | `string` | Username.  |  |
| `password` | `string` | Password.  |  |
| `start_date` | `string` | Start date.  |  |

## Streams
| Stream Name | Primary Key | Pagination | Supports Full Sync | Supports Incremental |
|-------------|-------------|------------|---------------------|----------------------|
| appointments | id | No pagination | ✅ |  ✅  |
| calendars | id | No pagination | ✅ |  ❌  |
| clients | email | No pagination | ✅ |  ❌  |
| appointment-types | id | No pagination | ✅ |  ❌  |
| blocks | id | No pagination | ✅ |  ✅  |
| labels | id | No pagination | ✅ |  ❌  |
| forms | id | No pagination | ✅ |  ❌  |

## IP allow list

If you use Airbyte Cloud and your organization restricts access to specific IPs, add the [Airbyte Cloud IP addresses](https://docs.airbyte.com/platform/operating-airbyte/ip-allowlist) to your allow list.

## Changelog

<details>
  <summary>Expand to review</summary>

| Version          | Date              | Pull Request | Subject        |
|------------------|-------------------|--------------|----------------|
| 0.0.2 | 2026-04-21 | [76492](https://github.com/airbytehq/airbyte/pull/76492) | Update dependencies |
| 0.0.1 | 2025-07-02 | | Initial release by [@chanronson](https://github.com/chanronson) via Connector Builder |

</details>

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

## Changelog

<details>
  <summary>Expand to review</summary>

| Version          | Date              | Pull Request | Subject        |
|------------------|-------------------|--------------|----------------|
| 0.0.1 | 2025-07-02 | | Initial release by [@chanronson](https://github.com/chanronson) via Connector Builder |

</details>

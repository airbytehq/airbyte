# Keka

The Keka connector syncs employee, attendance, leave, and project timesheet data from the [Keka API](https://developers.keka.com/) to your destination.

## Prerequisites

- A Keka API subscription. Keka API access is an add-on feature.
- Global admin access in Keka. Only Global admins can generate and manage API keys.
- Your company's Keka subdomain. For `https://acme.keka.com`, the subdomain is `acme`.

## Set up the Keka connector

### Step 1: Generate API credentials in Keka

1. In Keka, go to **Global admin settings** > **Integrations & Automations** > **API access** > **API key**.
2. Generate an API key. Keka shows the client ID, client secret, and API key for your account.
3. Configure the API key's scopes to cover the data you want to sync. Keka assigns scopes per API key, and an access token can only read data that the key's scopes allow. The available scopes are Employee And Org Information, Leave, Attendance, Payroll, Timesheet, and Performance.

For more information, see [Keka's getting started guide](https://developers.keka.com/docs/getting-started-for-customers).

### Step 2: Configure the connector in Airbyte

| Input           | Type     | Description                                                    |
| --------------- | -------- | -------------------------------------------------------------- |
| `subdomain`     | `string` | Your company subdomain, without `https://` or `.keka.com`.     |
| `client_id`     | `string` | The client ID from your Keka API key.                          |
| `client_secret` | `string` | The client secret from your Keka API key.                      |
| `api_key`       | `string` | Your Keka API key.                                             |
| `grant_type`    | `string` | Enter `kekaapi`.                                               |
| `scope`         | `string` | Enter `kekaapi`.                                               |

The connector requests an access token from `https://login.keka.com/connect/token` and reads data from `https://<subdomain>.keka.com/api/v1`. Keka's sandbox environment (`kekademo.com`) isn't supported.

If you're upgrading from a version earlier than 0.1.0, follow the [migration guide](keka-migrations.md) to configure the company subdomain before syncing.

## Supported sync modes

The Keka connector supports [Full Refresh](https://docs.airbyte.com/platform/using-airbyte/core-concepts/sync-modes/full-refresh-overwrite) syncs only. It doesn't support incremental syncs.

## Supported streams

| Stream             | Keka API endpoint                                                                     | Primary key  |
| ------------------ | ------------------------------------------------------------------------------------- | ------------ |
| Employees          | [`/hris/employees`](https://developers.keka.com/reference/get_hris-employees)         |              |
| Attendance         | [`/time/attendance`](https://developers.keka.com/reference/get_time-attendance-1)     |              |
| Clients            | [`/psa/clients`](https://developers.keka.com/reference/get_psa-clients-1)             |              |
| Projects           | [`/psa/projects`](https://developers.keka.com/reference/get_psa-projects-1)           |              |
| Project Timesheets | [`/psa/timeentries`](https://developers.keka.com/reference/get_psa-timeentries)       |              |
| Leave Type         | [`/time/leavetypes`](https://developers.keka.com/reference/get_time-leavetypes)       | `identifier` |
| Leave Request      | [`/time/leaverequests`](https://developers.keka.com/reference/get_time-leaverequests) |              |

## Limitations

- **30-day window for date-based streams:** The connector doesn't send a date range, so the Attendance, Leave Request, and Project Timesheets streams return Keka's default: records from the last 30 days. Each sync reads all pages within that range, not the complete history.
- **Rate limits:** Keka allows 50 API requests per minute and returns a `429` error when you exceed the limit. The connector retries rate-limited requests with backoff. For details, see [Keka's rate limit documentation](https://developers.keka.com/reference/rate-limit).

## IP allow list

If you use Airbyte Cloud and your organization restricts access to specific IPs, add the [Airbyte Cloud IP addresses](https://docs.airbyte.com/platform/operating-airbyte/ip-allowlist) to your allow list.

## Changelog

<details>
  <summary>Expand to review</summary>

| Version | Date       | Pull Request                                             | Subject                                                                                             |
| ------- | ---------- | -------------------------------------------------------- | --------------------------------------------------------------------------------------------------- |
| 0.1.0   | 2026-10-09 | [88299](https://github.com/airbytehq/airbyte/pull/88299) | Require the company subdomain, correct pagination, and allow authentication requests.               |
| 0.0.56  | 2026-10-06 | [87915](https://github.com/airbytehq/airbyte/pull/87915) | Update dependencies                                                                                 |
| 0.0.55  | 2026-09-29 | [87199](https://github.com/airbytehq/airbyte/pull/87199) | Update dependencies                                                                                 |
| 0.0.54  | 2026-09-22 | [86688](https://github.com/airbytehq/airbyte/pull/86688) | Update dependencies                                                                                 |
| 0.0.53  | 2026-09-15 | [86112](https://github.com/airbytehq/airbyte/pull/86112) | Update dependencies                                                                                 |
| 0.0.52  | 2026-09-08 | [85545](https://github.com/airbytehq/airbyte/pull/85545) | Update dependencies                                                                                 |
| 0.0.51  | 2026-08-18 | [84630](https://github.com/airbytehq/airbyte/pull/84630) | Update dependencies                                                                                 |
| 0.0.50  | 2026-08-11 | [83994](https://github.com/airbytehq/airbyte/pull/83994) | Update dependencies                                                                                 |
| 0.0.49  | 2026-08-04 | [83510](https://github.com/airbytehq/airbyte/pull/83510) | Update dependencies                                                                                 |
| 0.0.48  | 2026-07-28 | [82966](https://github.com/airbytehq/airbyte/pull/82966) | Update dependencies                                                                                 |
| 0.0.47  | 2026-07-21 | [82460](https://github.com/airbytehq/airbyte/pull/82460) | Update dependencies                                                                                 |
| 0.0.46  | 2026-07-14 | [81880](https://github.com/airbytehq/airbyte/pull/81880) | Update dependencies                                                                                 |
| 0.0.45  | 2026-06-30 | [81118](https://github.com/airbytehq/airbyte/pull/81118) | Update dependencies                                                                                 |
| 0.0.44  | 2026-06-23 | [80519](https://github.com/airbytehq/airbyte/pull/80519) | Update dependencies                                                                                 |
| 0.0.43  | 2026-06-16 | [79925](https://github.com/airbytehq/airbyte/pull/79925) | Update dependencies                                                                                 |
| 0.0.42  | 2026-06-09 | [79363](https://github.com/airbytehq/airbyte/pull/79363) | Update dependencies                                                                                 |
| 0.0.41  | 2026-06-02 | [78789](https://github.com/airbytehq/airbyte/pull/78789) | Update dependencies                                                                                 |
| 0.0.40  | 2026-04-28 | [77326](https://github.com/airbytehq/airbyte/pull/77326) | Update dependencies                                                                                 |
| 0.0.39  | 2026-04-21 | [76634](https://github.com/airbytehq/airbyte/pull/76634) | Update dependencies                                                                                 |
| 0.0.38  | 2026-03-31 | [75700](https://github.com/airbytehq/airbyte/pull/75700) | Update dependencies                                                                                 |
| 0.0.37  | 2026-03-24 | [74439](https://github.com/airbytehq/airbyte/pull/74439) | Update dependencies                                                                                 |
| 0.0.36  | 2026-03-03 | [74235](https://github.com/airbytehq/airbyte/pull/74235) | Update dependencies                                                                                 |
| 0.0.35  | 2026-02-17 | [73542](https://github.com/airbytehq/airbyte/pull/73542) | Update dependencies                                                                                 |
| 0.0.34  | 2026-02-10 | [73040](https://github.com/airbytehq/airbyte/pull/73040) | Update dependencies                                                                                 |
| 0.0.33  | 2026-02-03 | [72739](https://github.com/airbytehq/airbyte/pull/72739) | Update dependencies                                                                                 |
| 0.0.32  | 2026-01-20 | [71961](https://github.com/airbytehq/airbyte/pull/71961) | Update dependencies                                                                                 |
| 0.0.31  | 2026-01-14 | [71389](https://github.com/airbytehq/airbyte/pull/71389) | Update dependencies                                                                                 |
| 0.0.30  | 2025-12-18 | [70772](https://github.com/airbytehq/airbyte/pull/70772) | Update dependencies                                                                                 |
| 0.0.29  | 2025-11-25 | [69502](https://github.com/airbytehq/airbyte/pull/69502) | Update dependencies                                                                                 |
| 0.0.28  | 2025-10-29 | [68521](https://github.com/airbytehq/airbyte/pull/68521) | Update dependencies                                                                                 |
| 0.0.27  | 2025-10-14 | [67974](https://github.com/airbytehq/airbyte/pull/67974) | Update dependencies                                                                                 |
| 0.0.26  | 2025-10-07 | [67355](https://github.com/airbytehq/airbyte/pull/67355) | Update dependencies                                                                                 |
| 0.0.25  | 2025-09-30 | [66804](https://github.com/airbytehq/airbyte/pull/66804) | Update dependencies                                                                                 |
| 0.0.24  | 2025-09-09 | [66103](https://github.com/airbytehq/airbyte/pull/66103) | Update dependencies                                                                                 |
| 0.0.23  | 2025-08-23 | [65386](https://github.com/airbytehq/airbyte/pull/65386) | Update dependencies                                                                                 |
| 0.0.22  | 2025-08-09 | [64621](https://github.com/airbytehq/airbyte/pull/64621) | Update dependencies                                                                                 |
| 0.0.21  | 2025-08-02 | [64243](https://github.com/airbytehq/airbyte/pull/64243) | Update dependencies                                                                                 |
| 0.0.20  | 2025-07-26 | [63908](https://github.com/airbytehq/airbyte/pull/63908) | Update dependencies                                                                                 |
| 0.0.19  | 2025-07-19 | [63459](https://github.com/airbytehq/airbyte/pull/63459) | Update dependencies                                                                                 |
| 0.0.18  | 2025-07-12 | [63145](https://github.com/airbytehq/airbyte/pull/63145) | Update dependencies                                                                                 |
| 0.0.17  | 2025-07-05 | [62645](https://github.com/airbytehq/airbyte/pull/62645) | Update dependencies                                                                                 |
| 0.0.16  | 2025-06-28 | [62172](https://github.com/airbytehq/airbyte/pull/62172) | Update dependencies                                                                                 |
| 0.0.15  | 2025-06-21 | [61849](https://github.com/airbytehq/airbyte/pull/61849) | Update dependencies                                                                                 |
| 0.0.14  | 2025-06-14 | [61129](https://github.com/airbytehq/airbyte/pull/61129) | Update dependencies                                                                                 |
| 0.0.13  | 2025-05-24 | [59800](https://github.com/airbytehq/airbyte/pull/59800) | Update dependencies                                                                                 |
| 0.0.12  | 2025-05-03 | [59247](https://github.com/airbytehq/airbyte/pull/59247) | Update dependencies                                                                                 |
| 0.0.11  | 2025-04-26 | [58796](https://github.com/airbytehq/airbyte/pull/58796) | Update dependencies                                                                                 |
| 0.0.10  | 2025-04-19 | [58156](https://github.com/airbytehq/airbyte/pull/58156) | Update dependencies                                                                                 |
| 0.0.9   | 2025-04-12 | [57690](https://github.com/airbytehq/airbyte/pull/57690) | Update dependencies                                                                                 |
| 0.0.8   | 2025-04-05 | [57093](https://github.com/airbytehq/airbyte/pull/57093) | Update dependencies                                                                                 |
| 0.0.7   | 2025-03-29 | [56700](https://github.com/airbytehq/airbyte/pull/56700) | Update dependencies                                                                                 |
| 0.0.6   | 2025-03-22 | [55498](https://github.com/airbytehq/airbyte/pull/55498) | Update dependencies                                                                                 |
| 0.0.5   | 2025-03-01 | [54766](https://github.com/airbytehq/airbyte/pull/54766) | Update dependencies                                                                                 |
| 0.0.4   | 2025-02-22 | [54328](https://github.com/airbytehq/airbyte/pull/54328) | Update dependencies                                                                                 |
| 0.0.3   | 2025-02-15 | [53861](https://github.com/airbytehq/airbyte/pull/53861) | Update dependencies                                                                                 |
| 0.0.2   | 2025-02-08 | [53271](https://github.com/airbytehq/airbyte/pull/53271) | Update dependencies                                                                                 |
| 0.0.1   | 2025-01-29 |                                                          | Initial release by [@bhushan-barbuddhe](https://github.com/bhushan-barbuddhe) via Connector Builder |

</details>

# Hibob

This page contains the setup guide and reference information for the Hibob source connector.

## Prerequisites

- A [HiBob account](https://www.hibob.com)
- A HiBob API service user ID and token
- The service user must have access to the employee, metadata, employee table history, time off, and job catalog data you want to sync

## Setup guide

### Step 1: Create a HiBob API service user

Create a HiBob API service user and copy the service user ID and token. For details, see the [HiBob authentication documentation](https://apidocs.hibob.com/docs/authentication).

### Step 2: Configure the source in Airbyte

1. In Airbyte, select **Sources** and then select **New source**.
2. Select **HiBob**.
3. Enter the service user ID as **Service user ID**.
4. Enter the service user token as **Service user token**.
5. Toggle **Use sandbox** if the credentials belong to a HiBob sandbox account.
6. Optionally set **Start date** for the `time_off_request_changes` incremental stream.
7. Select **Set up source**.

## Supported sync modes

The HiBob source connector supports the following sync modes:

- Full Refresh - Overwrite
- Full Refresh - Append
- Incremental - Append + Deduped for `time_off_request_changes`

## Supported streams

- `employees`: core employee records from `POST /people/search`
- `profiles`: public active employee profiles from `GET /profiles`
- `employee_fields`: employee field metadata from `GET /company/people/fields`
- `company_named_lists`: named list metadata from `GET /company/named-lists`
- `work_history`: work table history from `GET /bulk/people/work`
- `lifecycle_history`: lifecycle table history from `GET /bulk/people/lifecycle`
- `employment_history`: employment table history from `GET /bulk/people/employment`
- `time_off_request_changes`: time off request changes from `GET /timeoff/requests/changes`
- `job_roles`: job catalog roles from `GET /job-catalog/job-roles`

## Changelog

<details>
  <summary>Expand to review</summary>

| Version  | Date       | Pull Request | Subject |
|:---------|:-----------|:-------------|:--------|
| 1.0.0 | 2026-05-14 | TBD | Rebuild connector against the current HiBob public API |
| 0.2.48 | 2026-04-28 | [77270](https://github.com/airbytehq/airbyte/pull/77270) | Update dependencies |
| 0.2.47 | 2026-04-21 | [76618](https://github.com/airbytehq/airbyte/pull/76618) | Update dependencies |
| 0.2.46 | 2026-03-31 | [75735](https://github.com/airbytehq/airbyte/pull/75735) | Update dependencies |
| 0.2.45 | 2026-03-24 | [75352](https://github.com/airbytehq/airbyte/pull/75352) | Update dependencies |
| 0.2.44 | 2026-03-10 | [74683](https://github.com/airbytehq/airbyte/pull/74683) | Update dependencies |
| 0.2.43 | 2026-02-24 | [73966](https://github.com/airbytehq/airbyte/pull/73966) | Update dependencies |
| 0.2.42 | 2026-02-03 | [72636](https://github.com/airbytehq/airbyte/pull/72636) | Update dependencies |
| 0.2.41 | 2026-01-20 | [71872](https://github.com/airbytehq/airbyte/pull/71872) | Update dependencies |
| 0.2.40 | 2026-01-14 | [71734](https://github.com/airbytehq/airbyte/pull/71734) | Update dependencies |

</details>

# Rippling

This page contains the setup guide and reference information for the [Rippling](https://www.rippling.com) source connector.

Rippling runs HR, payroll, IT and finance in one system. This connector reads workers, users and org structure (departments, teams, titles, levels, work locations, legal entities), compensation, time and leave, devices and app accounts, recruiting and headcount data, custom objects, the worker change feed and the activity log from the [Rippling REST Platform API v2](https://developer.rippling.com/documentation/rest-api) at `https://rest.ripplingapis.com`.

## Prerequisites

- A Rippling account with API access. Rippling lists **API Tier 1** as the requirement for most endpoints; `worker_changes` and `worker_change_fields` require the **Worker Changes API**, and `activity_log` requires the **Activity Log Platform API**.
- A Rippling API token. Tokens are created in **Tools > Developer > API Tokens** and can only read what the token owner's permission profile and the token's scopes allow. See [API tokens and permissions](https://developer.rippling.com/documentation/rest-api/essentials/api-tokens).

## Setup guide

### Step 1: Create a Rippling API token

1. In Rippling, open **Tools > Developer > API Tokens** and create a token.
2. Select the read scopes for the streams you want to sync (see the table below). Streams whose scope is missing fail with a clear error, so either add the scope or deselect the stream.
3. Use an owner whose permission profile can see the workers and fields you need. Rippling revokes a token when its owner is terminated or when it has not been used for 30 days.

### Step 2: Set up the Rippling connector in Airbyte

#### For Airbyte Cloud

1. [Log into your Airbyte Cloud](https://cloud.airbyte.com/workspaces) account.
2. In the left navigation bar, click **Sources**. In the top-right corner, click **+ New source**.
3. On the Set up the source page, select **Rippling** from the Source type dropdown.
4. Enter a name for the Rippling connector.
5. Enter the **API Token**.
6. (Optional) Enter a **Start Date** in `YYYY-MM-DDTHH:MM:SSZ` format. On the first sync, incremental streams only read records changed on or after this time. Leave it empty to read the full history.
7. (Optional) Set **API Version** to pin a different dated Rippling API version. The default is `2024-08-01`, the version the official Rippling SDK sends.
8. Click **Set up source**.

#### For Airbyte Open Source

1. Navigate to the Airbyte Open Source dashboard.
2. In the left navigation bar, click **Sources**. In the top-right corner, click **+ New source**.
3. On the Set up the source page, select **Rippling** from the Source type dropdown.
4. Enter a name for the Rippling connector.
5. Fill in the fields as described for Airbyte Cloud above.
6. Click **Set up source**.

## Supported sync modes

| Feature                       | Supported? |
| :---------------------------- | :--------- |
| Full Refresh Sync             | Yes        |
| Incremental Sync              | Yes        |
| Replicate Incremental Deletes | No         |
| SSL connection                | Yes        |
| Namespaces                    | No         |

## Supported streams

| Stream                     | Endpoint                                  | Primary key                | Sync modes                | Cursor      | Scope                             | Rippling plan             |
| :------------------------- | :---------------------------------------- | :------------------------- | :------------------------ | :---------- | :-------------------------------- | :------------------------ |
| companies                  | `GET /companies/`                         | id                         | Full Refresh              |             | `companies.read`                  | API Tier 1                |
| workers                    | `GET /workers/`                           | id                         | Full Refresh, Incremental | updated_at  | `workers.read`                    | API Tier 1                |
| users                      | `GET /users/`                             | id                         | Full Refresh              |             | `users.read`                      | API Tier 1                |
| compensations              | `GET /compensations/`                     | id                         | Full Refresh              |             | `compensations.read`              | API Tier 1                |
| employment_types           | `GET /employment-types/`                  | id                         | Full Refresh              |             | `employment-types.read`           | API Tier 1                |
| custom_fields              | `GET /custom-fields/`                     | id                         | Full Refresh              |             | `custom-fields.read`              | API Tier 1                |
| departments                | `GET /departments/`                       | id                         | Full Refresh              |             | `departments.read`                | API Tier 1                |
| teams                      | `GET /teams/`                             | id                         | Full Refresh              |             | `teams.read`                      | API Tier 1                |
| titles                     | `GET /titles/`                            | id                         | Full Refresh              |             | `titles.read`                     | API Tier 1                |
| levels                     | `GET /levels/`                            | id                         | Full Refresh              |             | `levels.read`                     | API Tier 1                |
| tracks                     | `GET /tracks/`                            | id                         | Full Refresh              |             | `tracks.read`                     | API Tier 1                |
| job_functions              | `GET /job-functions/`                     | id                         | Full Refresh              |             | `job-functions.read`              | API Tier 1                |
| work_locations             | `GET /work-locations/`                    | id                         | Full Refresh              |             | `work-locations.read`             | API Tier 1                |
| legal_entities             | `GET /legal-entities/`                    | id                         | Full Refresh              |             |                                   | API Tier 1                |
| business_partners          | `GET /business-partners/`                 | id                         | Full Refresh              |             | `business-partners.read`          | API Tier 1                |
| business_partner_groups    | `GET /business-partner-groups/`           | id                         | Full Refresh              |             | `business-partner-groups.read`    | API Tier 1                |
| supergroups                | `GET /supergroups/`                       | id                         | Full Refresh              |             | `supergroups.read`                | API Tier 1                |
| leave_types                | `GET /leave-types/`                       | id                         | Full Refresh              |             | `leave-types.read`                | API Tier 1                |
| leave_requests             | `GET /leave-requests/`                    | id                         | Full Refresh              |             | `leave-requests.read`             | API Tier 1                |
| leave_balances             | `GET /leave-balances/`                    | id                         | Full Refresh              |             | `leave-balances.read`             | API Tier 1                |
| time_entries               | `GET /time-entries/`                      | id                         | Full Refresh, Incremental | updated_at  | `time-entries.read`               | API Tier 1                |
| time_cards                 | `GET /time-cards/`                        | id                         | Full Refresh              |             | `time-cards.read`                 | API Tier 1                |
| worker_time_splits         | `GET /worker-time-splits/`                | id                         | Full Refresh, Incremental | updated_at  | `worker-time-splits.read`         | API Tier 1                |
| schedules                  | `GET /schedules/`                         | id                         | Full Refresh              |             | `schedules.read`                  | API Tier 1                |
| devices                    | `GET /devices/`                           | id                         | Full Refresh              |             | `devices.read`                    | API Tier 1                |
| app_users                  | `GET /app-users/`                         | id                         | Full Refresh, Incremental | updated_at  | `app-users.read`                  | API Tier 1                |
| software_deployments       | `GET /software-deployments/`              | id                         | Full Refresh              |             | `software-deployments.read`       | API Tier 1                |
| job_requisitions           | `GET /job-requisitions/`                  | id                         | Full Refresh              |             | `job-requisitions.read`           | API Tier 1                |
| headcount_positions        | `GET /headcount-positions/`               | id                         | Full Refresh              |             | `headcount-positions.read`        | API Tier 1                |
| compensation_bands_details | `GET /compensation-bands-details/`        | id                         | Full Refresh, Incremental | updated_at  | `compensation-bands-details.read` | API Tier 1                |
| object_categories          | `GET /object-categories/`                 | id                         | Full Refresh              |             | `custom-objects.read`             | API Tier 1                |
| custom_objects             | `GET /custom-objects/`                    | id                         | Full Refresh              |             | `custom-objects.read`             | API Tier 1                |
| custom_object_records      | `GET /custom-objects/{api_name}/records/` | custom_object_api_name, id | Full Refresh              |             | `custom-object-records.read`      | API Tier 1                |
| worker_change_fields       | `GET /worker-change-fields/`              | field_key                  | Full Refresh              |             |                                   | Worker Changes API        |
| worker_changes             | `GET /worker-changes/`                    | id                         | Full Refresh, Incremental | applied_on  |                                   | Worker Changes API        |
| activity_log               | `GET /activity-log/`                      | id                         | Full Refresh, Incremental | occurred_at | `activity-log.read`               | Activity Log Platform API |

### Incremental streams

Seven streams sync incrementally using the API's server-side `filter` parameter, for example `filter=updated_at ge 2026-01-01T00:00:00&order_by=updated_at asc`, so each sync only requests records changed since the previous one. The filter is sent with second precision. Records changed within the same second as the saved cursor can be read again, and Append + Deduped sync mode removes those duplicates.

- `worker_changes` uses `applied_on`, the time Rippling saved or approved the change, as Rippling recommends for polling the change feed. Changes with a future `effective_on` date are still picked up when they are saved.
- `activity_log` uses `occurred_at`. Rippling only keeps the last 90 days of activity log events, so the connector never requests events older than 89 days, even when the start date or saved state is older.

### Notes

- Related objects such as `worker.user` or `worker.department` are returned as IDs. The expanded object fields are kept in the schema but are `null`, because the connector does not request `expand`.
- `custom_object_records` reads the records of every custom object returned by `custom_objects` and adds a `custom_object_api_name` field, which is part of the primary key.
- Rippling can return `null` for fields the token owner is not allowed to see.

## Limitations and performance considerations

Rippling allows 600 requests per 10 seconds per token and endpoint path. The connector requests 100 records per page (the documented maximum), runs 3 streams in parallel by default (configurable up to 10), and retries HTTP 429 and 5xx responses, honoring `Retry-After` and otherwise backing off exponentially.

## Changelog

<details>
  <summary>Expand to review</summary>

| Version | Date       | Pull Request                                             | Subject              |
| :------ | :--------- | :------------------------------------------------------- | :------------------- |
| 0.1.0   | 2026-11-04 | [90987](https://github.com/airbytehq/airbyte/pull/90987) | New Source: Rippling |

</details>

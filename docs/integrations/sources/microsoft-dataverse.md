# Microsoft Dataverse

This source syncs data from [Microsoft Dataverse](https://learn.microsoft.com/en-us/power-apps/developer/data-platform/overview) using the [Dataverse Web API](https://learn.microsoft.com/en-us/power-apps/developer/data-platform/webapi/overview) (v9.2).

## Prerequisites

- A Microsoft Dataverse environment (included with Dynamics 365 or Power Apps)
- An [app registration](https://learn.microsoft.com/en-us/power-apps/developer/data-platform/walkthrough-register-app-azure-active-directory) in Microsoft Entra ID (formerly Azure Active Directory) with a client secret
- The app registration must be added as an [application user](https://learn.microsoft.com/en-us/power-apps/developer/data-platform/authenticate-oauth) in your Dataverse environment with at least read access to the tables you want to sync

## Setup guide

### Step 1: Register an application in Microsoft Entra ID

1. Sign in to the [Azure portal](https://portal.azure.com).
2. Navigate to **Microsoft Entra ID** > **App registrations** > **New registration**.
3. Enter a name for the application and select **Register**.
4. Note the **Application (client) ID** and **Directory (tenant) ID** from the Overview page.
5. Under **Certificates & secrets**, select **New client secret**, add a description and expiry, then select **Add**. Copy the secret **Value** immediately — it won't be shown again.

### Step 2: Add the application user to Dataverse

1. Sign in to the [Power Platform admin center](https://admin.powerplatform.microsoft.com).
2. Select your environment, then select **Settings** > **Users + permissions** > **Application users**.
3. Select **New app user**, find your app registration, assign it a business unit, and grant it a security role with read privileges on the tables you want to sync.

### Step 3: Configure the connector in Airbyte

Provide the following fields:

| Field | Description |
| :---- | :---------- |
| **URL** | Your Dataverse environment URL, for example `https://yourorg.crm.dynamics.com`. Do not include a trailing slash or path. |
| **Tenant ID** | The Directory (tenant) ID from your app registration. |
| **Client ID** | The Application (client) ID from your app registration. |
| **Client Secret** | The client secret value you created in Step 1. |
| **Max page size** | Maximum number of records per API response page (default: 5000). Reduce this value if you encounter timeout errors on tables with wide rows. |

## Supported streams

The connector automatically discovers all tables (entities) in your Dataverse environment using the [EntityDefinitions](https://learn.microsoft.com/en-us/power-apps/developer/data-platform/webapi/reference/entitymetadata) API. Each table becomes an available stream.

### Sync modes

| Feature | Supported | Notes |
| :------ | :-------- | :---- |
| Full Refresh | Yes | Available for all tables. |
| Incremental Sync | Yes | Available for tables with [change tracking](https://learn.microsoft.com/en-us/power-apps/developer/data-platform/use-change-tracking-synchronize-data-external-systems) enabled. Uses OData delta tokens to fetch only modified and deleted records. |
| Replicate Incremental Deletes | Yes | Deleted records are emitted with only the primary key populated. |
| Namespaces | No | |

For incremental sync, the connector uses Dataverse's change tracking feature (`Prefer: odata.track-changes` header). The API returns a `@odata.deltaLink` on the last page of results, which the connector stores as state and uses on subsequent syncs to retrieve only changes since the last sync.

### Data type mapping

| Dataverse Type | Airbyte Type | Notes |
| :------------- | :----------- | :---- |
| `String` | `string` | |
| `UniqueIdentifier` | `string` | |
| `DateTime` (DateOnly behavior) | `date` | Fields with `DateTimeBehavior=DateOnly` |
| `DateTime` (other behaviors) | `timestamp_with_timezone` | `UserLocal` and `TimeZoneIndependent` behaviors |
| `Integer` | `integer` | |
| `BigInt` | `integer` | |
| `Money` | `number` | |
| `Boolean` | `boolean` | |
| `Double` | `number` | |
| `Decimal` | `number` | |
| `Picklist` | `integer` | |
| `Status` | `integer` | |
| `State` | `integer` | |
| `Lookup` | `string` | Field name is prefixed with `_` and suffixed with `_value` (for example, `_ownerid_value`). |
| `Virtual` | — | Skipped; not synced. |

All other types default to `string`.

## Limitations and known issues

- **Change tracking must be enabled** on a table for incremental sync to be available. Tables without change tracking support only full refresh. You can [enable change tracking](https://learn.microsoft.com/en-us/power-apps/maker/data-platform/data-platform-create-entity#enable-change-tracking) in the Power Apps table settings.
- **Virtual fields** are excluded from the schema and not synced.
- **Service protection limits**: Dataverse enforces [API service protection limits](https://learn.microsoft.com/en-us/power-apps/developer/data-platform/api-limits) that return HTTP 429 when exceeded. The connector handles back-off automatically. If you run into persistent throttling, reduce the **Max page size** or schedule syncs during off-peak hours.

## IP allow list

If you use Airbyte Cloud and your organization restricts access to specific IPs, add the [Airbyte Cloud IP addresses](https://docs.airbyte.com/platform/operating-airbyte/ip-allowlist) to your allow list.

## Changelog

<details>
  <summary>Expand to review</summary>

| Version | Date       | Pull Request                                             | Subject                                                                                |
| :------ | :--------- | :------------------------------------------------------- | :------------------------------------------------------------------------------------- |
| 1.0.3 | 2026-07-21 | [79418](https://github.com/airbytehq/airbyte/pull/79418) | Update dependencies |
| 1.0.2 | 2026-06-07 | [79143](https://github.com/airbytehq/airbyte/pull/79143) | Revert connector base image to 4.0.0 (4.1.0 ships Python 3.13, incompatible with the connector's pinned CDK). |
| 1.0.1 | 2026-06-02 | [78805](https://github.com/airbytehq/airbyte/pull/78805) | Update dependencies |
| 1.0.0 | 2026-05-13 | [77565](https://github.com/airbytehq/airbyte/pull/77565) | Map DateOnly fields to `date` format instead of `date-time`. Add `$select` projection to discovery to reduce metadata payload size. Streams with DateOnly fields require a schema refresh and data reset. |
| 0.1.32 | 2025-05-10 | [60052](https://github.com/airbytehq/airbyte/pull/60052) | Update dependencies |
| 0.1.31 | 2025-05-03 | [59292](https://github.com/airbytehq/airbyte/pull/59292) | Update dependencies |
| 0.1.30 | 2025-04-26 | [58830](https://github.com/airbytehq/airbyte/pull/58830) | Update dependencies |
| 0.1.29 | 2025-04-19 | [57684](https://github.com/airbytehq/airbyte/pull/57684) | Update dependencies |
| 0.1.28 | 2025-04-05 | [57100](https://github.com/airbytehq/airbyte/pull/57100) | Update dependencies |
| 0.1.27 | 2025-03-29 | [56631](https://github.com/airbytehq/airbyte/pull/56631) | Update dependencies |
| 0.1.26 | 2025-03-22 | [56043](https://github.com/airbytehq/airbyte/pull/56043) | Update dependencies |
| 0.1.25 | 2025-03-08 | [55454](https://github.com/airbytehq/airbyte/pull/55454) | Update dependencies |
| 0.1.24 | 2025-03-01 | [54768](https://github.com/airbytehq/airbyte/pull/54768) | Update dependencies |
| 0.1.23 | 2025-02-22 | [54356](https://github.com/airbytehq/airbyte/pull/54356) | Update dependencies |
| 0.1.22 | 2025-02-15 | [46493](https://github.com/airbytehq/airbyte/pull/46493) | Update dependencies |
| 0.1.21 | 2024-09-26 | [45938](https://github.com/airbytehq/airbyte/pull/45938) | Make Dataverse available on Airbyte Cloud |
| 0.1.20 | 2024-09-21 | [45777](https://github.com/airbytehq/airbyte/pull/45777) | Update dependencies |
| 0.1.19 | 2024-09-14 | [45482](https://github.com/airbytehq/airbyte/pull/45482) | Update dependencies |
| 0.1.18 | 2024-09-07 | [45224](https://github.com/airbytehq/airbyte/pull/45224) | Update dependencies |
| 0.1.17 | 2024-08-31 | [44987](https://github.com/airbytehq/airbyte/pull/44987) | Update dependencies |
| 0.1.16 | 2024-08-24 | [44640](https://github.com/airbytehq/airbyte/pull/44640) | Update dependencies |
| 0.1.15 | 2024-08-17 | [44224](https://github.com/airbytehq/airbyte/pull/44224) | Update dependencies |
| 0.1.14 | 2024-08-10 | [43653](https://github.com/airbytehq/airbyte/pull/43653) | Update dependencies |
| 0.1.13 | 2024-08-03 | [43164](https://github.com/airbytehq/airbyte/pull/43164) | Update dependencies |
| 0.1.12 | 2024-07-27 | [42612](https://github.com/airbytehq/airbyte/pull/42612) | Update dependencies |
| 0.1.11 | 2024-07-20 | [42373](https://github.com/airbytehq/airbyte/pull/42373) | Update dependencies |
| 0.1.10 | 2024-07-13 | [41920](https://github.com/airbytehq/airbyte/pull/41920) | Update dependencies |
| 0.1.9 | 2024-07-10 | [41346](https://github.com/airbytehq/airbyte/pull/41346) | Update dependencies |
| 0.1.8 | 2024-07-09 | [41247](https://github.com/airbytehq/airbyte/pull/41247) | Update dependencies |
| 0.1.7 | 2024-07-06 | [40800](https://github.com/airbytehq/airbyte/pull/40800) | Update dependencies |
| 0.1.6 | 2024-06-25 | [40340](https://github.com/airbytehq/airbyte/pull/40340) | Update dependencies |
| 0.1.5 | 2024-06-21 | [39931](https://github.com/airbytehq/airbyte/pull/39931) | Update dependencies |
| 0.1.4 | 2024-06-06 | [39265](https://github.com/airbytehq/airbyte/pull/39265) | [autopull] Upgrade base image to v1.2.2 |
| 0.1.3 | 2024-05-20 | [38397](https://github.com/airbytehq/airbyte/pull/38397) | [autopull] base image + poetry + up_to_date |
| 0.1.2 | 2023-08-24 | [29732](https://github.com/airbytehq/airbyte/pull/29732) | Adjust source_default_cursor when modifiedon not exists |
| 0.1.1 | 2023-03-16 | [22805](https://github.com/airbytehq/airbyte/pull/22805) | Fixed deduped cursor field value update |
| 0.1.0 | 2022-11-14 | [18646](https://github.com/airbytehq/airbyte/pull/18646) | New Source: Microsoft Dataverse |

</details>

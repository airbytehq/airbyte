# Zoho CRM

## Sync overview

The Zoho CRM source supports both Full Refresh and Incremental syncs. You can choose if this connector will copy only the new or updated data, or all rows in the tables and columns you set up for replication, every time a sync is run.

The connector reads data through version 2 of the [Zoho CRM REST API](https://www.zoho.com/crm/developer/docs/api/v2/modules-api.html).

### Output schema

This Source is capable of syncing:

- standard modules available in Zoho CRM account
- custom modules manually added by user, available in Zoho CRM account
- custom fields in both standard and custom modules, available in Zoho CRM account

The discovering of Zoho CRM module schema is made dynamically based on Metadata API and should generally take no longer than 10 to 30 seconds.

### Notes:

Some of Zoho CRM Modules may not be available for sync due to limitations of Zoho CRM Edition or permissions scope. For details refer to the [Scopes](https://www.zoho.com/crm/developer/docs/api/v2/scopes.html) section in the Zoho CRM documentation.

Connector streams and schemas are built dynamically on top of Metadata that is available from the REST API - please see [Modules API](https://www.zoho.com/crm/developer/docs/api/v2/modules-api.html), [Modules Metadata API](https://www.zoho.com/crm/developer/docs/api/v2/module-meta.html), [Fields Metadata API](https://www.zoho.com/crm/developer/docs/api/v2/field-meta.html).
The list of available streams is the list of Modules as long as Module Metadata is available for each of them from the Zoho CRM API, and Fields Metadata is available for each of the fields. If a module you want to sync is not available from this connector, it's because the Zoho CRM API does not make it available.

### Data type mapping

| Integration Type      | Airbyte Type | Notes                     |
| :-------------------- | :----------- | :------------------------ |
| `boolean`             | `boolean`    |                           |
| `double`              | `number`     |                           |
| `currency`            | `number`     |                           |
| `integer`             | `integer`    |                           |
| `profileimage`        | `string`     |                           |
| `picklist`            | `string`     | enum                      |
| `textarea`            | `string`     |                           |
| `website`             | `string`     | format: uri               |
| `date`                | `string`     | format: date              |
| `datetime`            | `string`     | format: date-time         |
| `text`                | `string`     |                           |
| `phone`               | `string`     |                           |
| `bigint`              | `string`     | airbyte_type: big_integer |
| `event_reminder`      | `string`     |                           |
| `email`               | `string`     | format: email             |
| `autonumber`          | `string`     | airbyte_type: big_integer |
| `jsonarray`           | `array`      |                           |
| `jsonobject`          | `object`     |                           |
| `multiselectpicklist` | `array`      |                           |
| `lookup`              | `object`     |                           |
| `ownerlookup`         | `object`     |                           |
| `RRULE`               | `object`     |                           |
| `ALARM`               | `object`     |                           |

Any other data type not listed in the table above will be treated as `string`.

Auto-number fields are the one exception to that table: when the field has a prefix or suffix configured in Zoho CRM, its values are plain strings such as `INV-1042`, so the connector drops the `big_integer` type and syncs them as strings.

### Features

| Feature                                   | Supported? \(Yes/No\) |
| :---------------------------------------- | :-------------------- |
| Full Refresh Overwrite Sync               | Yes                   |
| Full Refresh Append Sync                  | Yes                   |
| Incremental - Append Sync                 | Yes                   |
| Incremental - Append + Deduplication Sync | Yes                   |
| Namespaces                                | No                    |

### Incremental syncs

Every stream supports incremental syncs. The connector resolves the cursor field separately for each module, using the first of these fields that the module's field metadata exposes:

1. `Modified_Time`
2. `Action_Performed_Time`
3. `Created_Time`

Most modules use `Modified_Time`. Modules that don't expose it, such as `Actions_Performed`, use `Action_Performed_Time` instead. Because the cursor field varies by module, each stream stores its state under its own cursor field name.

To read only changed records, the connector sends the stored cursor value in the `If-Modified-Since` request header, advanced by one second so the last record of the previous sync isn't read again. Zoho CRM returns `304 Not Modified` when nothing changed, which the connector treats as an empty page. If a record has no value in the cursor field, the connector emits the record but doesn't advance the stream's state.

Every stream schema includes `id` and `Modified_Time`, even for modules that don't have a `Modified_Time` field. For those modules the column is always null, and the module's real cursor field carries the timestamp.

#### Start date

**Start Date** is optional and sets how far back the first incremental sync reads. If you leave it empty, the connector reads from `1970-01-01T00:00:00+00:00`. Use an ISO 8601 value, with or without a time and UTC offset: `2024-01-01`, `2024-01-01 13:00:00`, `2024-01-01T13:00:00-07:00`, and `2024-01-01T13:00:00Z` are all accepted.

Connector versions earlier than 0.1.4 can't parse UTC timestamps that end in `Z`, and fail the sync with `Invalid isoformat string`. Upgrade to 0.1.4 or later if your start date or saved cursor value uses that format.

## List of Supported Environments for Zoho CRM

### Production

| Environment | Base URL                |
| :---------- | :---------------------- |
| US          | https://zohoapis.com    |
| AU          | https://zohoapis.com.au |
| EU          | https://zohoapis.eu     |
| IN          | https://zohoapis.in     |
| CN          | https://zohoapis.com.cn |
| JP          | https://zohoapis.jp     |

### Sandbox

| Environment | Endpoint                        |
| :---------- | :------------------------------ |
| US          | https://sandbox.zohoapis.com    |
| AU          | https://sandbox.zohoapis.com.au |
| EU          | https://sandbox.zohoapis.eu     |
| IN          | https://sandbox.zohoapis.in     |
| CN          | https://sandbox.zohoapis.com.cn |
| JP          | https://sandbox.zohoapis.jp     |

### Developer

| Environment | Endpoint                          |
| :---------- | :-------------------------------- |
| US          | https://developer.zohoapis.com    |
| AU          | https://developer.zohoapis.com.au |
| EU          | https://developer.zohoapis.eu     |
| IN          | https://developer.zohoapis.in     |
| CN          | https://developer.zohoapis.com.cn |
| JP          | https://developer.zohoapis.jp     |

For more information about available environments, please visit [this page](https://www.zoho.com/crm/developer/sandbox.html?src=dev-hub)

### Performance considerations

Zoho CRM API calls consume credits, and each Zoho CRM edition has a credit limit in a 24-hour rolling window. Discovery is more expensive than it looks: the connector makes one call to list your modules, then two metadata calls per module (module metadata and field metadata). Take this into account when you set sync frequency. For the credit cost of each call, see [API limits](https://www.zoho.com/crm/developer/docs/api/v2/api-limits.html) in the Zoho CRM documentation.

The **Zoho CRM Edition** you select controls how many metadata requests the connector makes in parallel while it builds the list of streams:

| Edition      | Parallel requests |
| :----------- | :---------------- |
| Free         | 5                 |
| Standard     | 10                |
| Professional | 15                |
| Enterprise   | 20                |
| Ultimate     | 25                |

Select the edition your Zoho CRM account actually uses. Selecting a higher edition than you have can push the connector past your account's concurrency limit.

### Note about using the Zoho Developer Environment

The Zoho Developer environment API is inconsistent with production environment API. It contains about half of the modules supported in the production environment. Keep this in mind when pulling data from the Developer environment.

## Setup guide

To configure the connector, you need:

| Field                | Required | Notes                                                                                                   |
| :------------------- | :------- | :------------------------------------------------------------------------------------------------------ |
| Client ID            | Yes      | OAuth 2.0 client ID from the Zoho API console                                                           |
| Client Secret        | Yes      | OAuth 2.0 client secret from the Zoho API console                                                       |
| Refresh Token        | Yes      | OAuth 2.0 refresh token you generate from a grant token                                                 |
| Data Center Location | Yes      | The region that hosts your Zoho CRM account: `US`, `AU`, `EU`, `IN`, `CN`, or `JP`                      |
| Environment          | Yes      | `Production`, `Developer`, or `Sandbox`                                                                 |
| Zoho CRM Edition     | Yes      | Sets the connector's request concurrency. See [Performance considerations](#performance-considerations) |
| Start Date           | No       | See [Start date](#start-date)                                                                           |

The connector doesn't support the Airbyte OAuth button, so you generate the refresh token yourself using the steps below.

### Get Client ID, Client Secret, and Grant Token

1. Log into https://api-console.zoho.com/
2. Choose client
3. Enter the scopes the refresh and access tokens cover. The connector reads module and field metadata, then reads records from each module, so grant `ZohoCRM.settings.modules.READ`, `ZohoCRM.settings.fields.READ`, and read access to the record data, such as `ZohoCRM.modules.ALL`. **Make sure the scope covers every module you want to sync.** If the token lacks metadata access for a module, that module doesn't appear as a stream; if it lacks record access, the stream appears but the sync fails when it tries to read data.
4. Enter grant token's lifetime and description, click "Create".
5. Copy Grant token, close the popup and copy Client ID and Client Secret on the "Client Secret" tab.

### Create Refresh Token

For generating the refresh token, please refer to [this page](https://www.zoho.com/crm/developer/docs/api/v2/access-refresh.html).
Make sure to complete the auth flow quickly, as the initial token granted by Zoho CRM is only live for a few minutes before it can no longer be used to generate a refresh token.

## IP allow list

If you use Airbyte Cloud and your organization restricts access to specific IPs, add the [Airbyte Cloud IP addresses](https://docs.airbyte.com/platform/operating-airbyte/ip-allowlist) to your allow list.

## Changelog

<details>
  <summary>Expand to review</summary>

| Version | Date       | Pull Request                                             | Subject                                                                                                                                   |
| :------ | :--------- | :------------------------------------------------------- | :---------------------------------------------------------------------------------------------------------------------------------------- |
| 0.1.5 | 2026-08-25 | [79062](https://github.com/airbytehq/airbyte/pull/79062) | Update dependencies |
| 0.1.4 | 2026-08-24 | [80278](https://github.com/airbytehq/airbyte/pull/80278) | Fix incremental sync: tolerate `Z`-suffixed (UTC) cursor values and resolve cursor field per module instead of hardcoding `Modified_Time` |
| 0.1.3 | 2025-02-05 | [42864](https://github.com/airbytehq/airbyte/pull/42864) | Migrate to Poetry |
| 0.1.2 | 2023-03-19 | [23906](https://github.com/airbytehq/airbyte/pull/23906) | added support for the latest CDK, fixed SAT |
| 0.1.1 | 2023-03-15 | [24034](https://github.com/airbytehq/airbyte/pull/24034) | Set airbyte type to string for zoho autonumbers when they include prefix or suffix |
| 0.1.0 | 2022-04-06 | [11193](https://github.com/airbytehq/airbyte/pull/11193) | Initial release |

</details>

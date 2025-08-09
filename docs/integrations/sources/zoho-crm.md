# Zoho CRM

## Sync overview

The Zoho CRM source supports both Full Refresh and Incremental syncs. You can choose if this connector will copy only the new or updated data, or all rows in the tables and columns you set up for replication, every time a sync is run.

Airbyte uses [REST API](https://www.zoho.com/crm/developer/docs/api/v2/modules-api.html) to fetch data from Zoho CRM.

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

### Features

| Feature                                   | Supported? \(Yes/No\) |
| :---------------------------------------- | :-------------------- |
| Full Refresh Overwrite Sync               | Yes                   |
| Full Refresh Append Sync                  | Yes                   |
| Incremental - Append Sync                 | Yes                   |
| Incremental - Append + Deduplication Sync | Yes                   |
| Namespaces                                | No                    |

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

Also, Zoho CRM API calls are associated with credits, each Zoho CRM edition has a limit in a 24-hour rolling window, so please, consider it when configuring your connections.
More details about Zoho CRM API credit system can be found [here](https://www.zoho.com/crm/developer/docs/api/v2/api-limits.html).

### Note about using the Zoho Developer Environment

The Zoho Developer environment API is inconsistent with production environment API. It contains about half of the modules supported in the production environment. Keep this in mind when pulling data from the Developer environment.

## Setup Guide (Airbyte Open Source)

To set up a connection with a Zoho CRM source, you will need to choose start sync date, Zoho CRM edition, region and environment. The latest are described above. Except for those, you will need OAuth2.0 credentials - Client ID, Client Secret and Refresh Token.

### Get Client ID, Client Secret, and Grant Token

1. Log into https://api-console.zoho.com/
2. Choose client
3. Enter a scope the future refresh and access tokens will cover. For instance, it can be `ZohoCRM.modules.ALL, ZohoCRM.settings.ALL, ZohoCRM.settings.modules.ALL`. **Make sure the scope covers all needed modules**.
4. Enter grant token's lifetime and description, click "Create".
5. Copy Grant token, close the popup and copy Client ID and Client Secret on the "Client Secret" tab.

### Create Refresh Token

For generating the refresh token, please refer to [this page](https://www.zoho.com/crm/developer/docs/api/v2/access-refresh.html).
Make sure to complete the auth flow quickly, as the initial token granted by Zoho CRM is only live for a few minutes before it can no longer be used to generate a refresh token.

## Changelog

<details>
  <summary>Expand to review</summary>

| Version | Date       | Pull Request                                             | Subject                                                                            |
| :------ | :--------- | :------------------------------------------------------- |:-----------------------------------------------------------------------------------|
| 0.1.3   | 2024-07-30 | [42864](https://github.com/airbytehq/airbyte/pull/42864) | Migrate to Poetry                                                                  |
| 0.1.2   | 2023-03-09 | [23906](https://github.com/airbytehq/airbyte/pull/23906) | added support for the latest CDK, fixed SAT                                        |
| 0.1.1   | 2023-03-13 | [23818](https://github.com/airbytehq/airbyte/pull/23818) | Set airbyte type to string for zoho autonumbers when they include prefix or suffix |
| 0.1.0   | 2022-03-30 | [11193](https://github.com/airbytehq/airbyte/pull/11193) | Initial release                                                                    |

</details>
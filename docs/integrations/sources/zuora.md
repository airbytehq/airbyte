# Zuora

## Sync overview

The Zuora source supports both Full Refresh and Incremental syncs. You can choose if this connector will copy only the new or updated data, or all rows in the tables and columns you set up for replication, every time a sync is run.

Airbyte uses [REST API](https://www.zuora.com/developer/api-reference/#section/Introduction) to fetch data from Zuora. The REST API accepts [ZOQL \(Zuora Object Query Language\)](https://knowledgecenter.zuora.com/Central_Platform/Query/Export_ZOQL), a SQL-like language, to export the data.

### Output schema

This Source is capable of syncing:

* standard objects available in Zuora account
* custom objects manually added by user, available in Zuora Account
* custom fields in both standard and custom objects, available in Zuora Account

The discovering of Zuora Account objects schema may take a while, if you add the connection for the first time, and/or you need to refresh your list of available streams. Please take your time to wait and don't cancel this operation, usually it takes up to 5-10 min, depending on number of objects available in Zuora Account.

### Note:

Some of the Zuora Objects may not be available for sync due to limitations of Zuora Supscription Plan, Permissions. For details refer to the [Availability of Data Source Objects](https://knowledgecenter.zuora.com/DC_Developers/M_Export_ZOQL) section in the Zuora documentation.

### Data type mapping

| Integration Type | Airbyte Type | Notes |
| :--- | :--- | :--- |
| `decimal(22,9)` | `number` | float number |
| `decimal` | `number` | float number |
| `float` | `number` | float number |
| `double` | `number` | float number |
| `integer` | `number` |  |
| `int` | `number` |  |
| `bigint` | `number` |  |
| `smallint` | `number` |  |
| `timestamp` | `number` | number representation of the unix timestamp |
| `date` | `string` |  |
| `datetime` | `string` |  |
| `timestamp with time zone` | `string` |  |
| `picklist` | `string` |  |
| `text` | `string` |  |
| `varchar` | `string` |  |
| `zoql` | `object` |  |
| `binary` | `object` |  |
| `json` | `object` |  |
| `xml` | `object` |  |
| `blob` | `object` |  |
| `list` | `array` |  |
| `array` | `array` |  |
| `boolean` | `boolean` |  |
| `bool` | `boolean` |  |

Any other data type not listed in the table above will be treated as `string`.

### Features

| Feature | Supported?\(Yes/No\) | Notes |
| :--- | :--- | :--- |
| Full Refresh Overwrite Sync | Yes |  |
| Full Refresh Append Sync | Yes |  |
| Incremental - Append Sync | Yes |  |
| Incremental - Append + Deduplication Sync | Yes |  |
| Namespaces | No |  |

## Supported Environments for Zuora

| Environment | Supported?\(Yes/No\) | Notes |
| :--- | :--- | :--- |
| Production | Yes | Select from exising options while setup |
| Sandbox | Yes | Select from exising options while setup |

## Supported Data Query options

| Option | Supported?\(Yes/No\) | Notes |
| :--- | :--- | :--- |
| LIVE | Yes | Run data queries against Zuora live transactional databases |
| UNLIMITED | Yes | Run data queries against an optimized, replicated database at 12 hours freshness for high volume extraction use cases (Early Adoption, additionall access required, contact [Zuora Support](http://support.zuora.com/hc/en-us) in order to request this feature enabled for your account beforehand.) |

## List of Supported Environments for Zuora

### Production

| Environment | Endpoint |
| :--- | :--- |
| US Production | rest.zuora.com |
| US Cloud Production | rest.na.zuora.com |
| EU Production | rest.eu.zuora.com |

### Sandbox

| Environment | Endpoint |
| :--- | :--- |
| US API Sandbox | rest.apisandbox.zuora.com |
| US Cloud API Sandbox | rest.sandbox.na.zuora.com |
| US Central Sandbox | rest.test.zuora.com |
| EU API Sandbox | rest.sandbox.eu.zuora.com |
| EU Central Sandbox | rest.test.eu.zuora.com |

### Other

| Environment | Endpoint |
| :--- | :--- |
| US Performance Test | rest.pt1.zuora.com |

For more information about available environments, please visit [this page](https://knowledgecenter.zuora.com/BB_Introducing_Z_Business/D_Zuora_Environments)

### Performance considerations

If you experience the long time for sync operation, please consider:

* to increase the `window_in_days` parameter inside Zuora source configuration
* use the smaller date range by tuning `start_date` parameter.

### Note

Usually, the very first sync operation for all of the objects inside Zuora account takes up to 25-45-60 min, the more data you have, the more time you'll need.

## Setup Guide

### Create an API user role

1. Log in to your [Zuora account](https://www.zuora.com/).
2. In the top right corner of the Zuora dashboard, click on the profile icon and select `Administration` under the `Settings` category.
3. Click on `Manage User Roles` in the `Administration Settings` section.
4. Click on `Add new role` to create a new role and fill in the necessary information in the form.

### Assign the role to a user

1. From the `Administration` page, click on `Manage Users` in the `Users` section.
2. Click on the `+ New User` button to create a single user.
3. Fill in the form to create a user and assign the user to the role created in the `Create an API user role` section.
4. Activate the API user by following the email instructions you received upon user creation.

For more information, visit the [Create an API User page](https://knowledgecenter.zuora.com/Billing/Tenant_Management/A_Administrator_Settings/Manage_Users/Create_an_API_User) in the Zuora documentation.

### Create Client ID and Client Secret

1. From the `Administration` page, click on `Manage Users` in the `Users` section.
2. Click on the username of the API user you created earlier.
3. In the `OAuth Clients for REST API` section, click on the `+ New OAuth Client` button.
4. Enter a client name and description, and click `Save`.
5. A pop-up will open with your Client ID and Client Secret. Make a note of them because they will never be shown again. You will need them to configure the Zuora connector in Airbyte.

For further details, visit the [Zuora API OAuth page](https://knowledgecenter.zuora.com/Billing/Tenant_Management/A_Administrator_Settings/Manage_Users/API_OAuth_Access) in the Zuora documentation.

### Configure the Zuora Source connector in Airbyte

Use the retrieved `Client ID` and `Client Secret` to set up the Zuora Source connector in Airbyte. You will also need to configure the following fields:

- **Start Date**: Enter the start date for data extraction in the format `YYYY-MM-DD`. Only data created or modified after this date will be extracted.
- **Query Window (in days)**: Set the number of days for each data chunk, starting from the start date. A larger value means faster data fetching. For example, 0.1 signifies a few hours, while 364 equates to a year. The default is 90 days.
- **Tenant Endpoint Location**: Choose the correct endpoint based on your tenant's location. More information is available at [Zuora API Access](https://www.zuora.com/developer/api-reference/#section/Introduction/Access-to-the-API).
- **Data Query Type**: Select between `Live` or `Unlimited`. The `Unlimited` option provides an optimized, replicated database with 12 hours of freshness for high-volume extraction. Find more details at [Zuora Data Query Overview](https://knowledgecenter.zuora.com/Central_Platform/Query/Data_Query/A_Overview_of_Data_Query#Query_Processing_Limitations). The default is `Live`.

After filling in the necessary fields, complete the setup by testing and saving the connection.

## Changelog

| Version | Date | Pull Request | Subject |
| :--- | :--- | :--- | :--- |
| 0.1.3 | 2021-10-16 | [7053](https://github.com/airbytehq/airbyte/pull/7093) | Added support of `Unlimited` option for `Data Query` |
| 0.1.2 | 2021-10-11 | [6960](https://github.com/airbytehq/airbyte/pull/6960) | Change minimum value for `Window_in_days` to 1, instead of 30 |
| 0.1.1 | 2021-10-01 | [6575](https://github.com/airbytehq/airbyte/pull/6575) | Added OAuth support for Airbyte Cloud |
| 0.1.0 | 2021-08-01 | [4661](https://github.com/airbytehq/airbyte/pull/4661) | Initial release of Native Zuora connector for Airbyte |


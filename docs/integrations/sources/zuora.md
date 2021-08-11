# Zuora

## Sync overview

The Zuora source supports both Full Refresh and Incremental syncs. You can choose if this connector will copy only the new or updated data, or all rows in the tables and columns you set up for replication, every time a sync is run.

Airbyte uses [REST API](https://www.zuora.com/developer/api-reference/#section/Introduction) to fetch data from Zuora. The REST API accepts [ZOQL (Zuora Object Query Language)](https://knowledgecenter.zuora.com/Central_Platform/Query/Export_ZOQL), a SQL-like language, to export the data.

This Source Connector is based on a [Airbyte CDK](https://docs.airbyte.io/connector-development/cdk-python).

### Output schema

This Source is capable of syncing:

* standard objects available in Zuora account
* custom objects manually added by user, available in Zuora Account
* custom fields in both standard and custom objects, available in Zuora Account

The discovering of Zuora Account objects schema may take a while, if you add the connection for the first time, and/or you need to refresh your list of available streams. Please take your time to wait and don't cancel this operation, usually it takes up to 5-10 min, depending on number of objects available in Zuora Account.

### Note:
Some of the Zuora Objects may not be available for sync due to limitations of Zuora Supscription Plan, Permissions.
For details refer to the [Availability of Data Source Objects](https://knowledgecenter.zuora.com/DC_Developers/M_Export_ZOQL) section in the Zuora documentation.


### Data type mapping

| Integration Type | Airbyte Type | Notes |
| :--- | :--- | :--- |
| `decimal(22,9)` | `number` | float number |
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
| Full Refresh Append Sync  | Yes |  |
| Incremental - Append Sync | Yes |  |
| Incremental - Append + Deduplication Sync | Yes |  |
| Namespaces | No |  |

## Supported Environments for Zuora
| Environment | Supported?\(Yes/No\) | Notes |
| :--- | :--- | :--- |
| Production | Yes | Default setting for the connector|
| Sandbox | Yes | Enable the `is_sandbox` toggle inside connector settings |

For more information about available environments, please visit [this page](https://knowledgecenter.zuora.com/BB_Introducing_Z_Business/D_Zuora_Environments)

### Performance considerations

If you experience the long time for sync operation, please consider:
* to increase the `window_in_days` parameter inside Zuora source configuration
* use the smaller date range by tuning `start_date` parameter.

### Note
Usually, the very first sync operation for all of the objects inside Zuora account takes up to 25-45-60 min, the more data you have, the more time you'll need.

## Getting started

### Create an API user role
1. Log in to your `Zuora acccount`.
2. In the top right corner of the Zuora dashboard, select `Settings` > `Administration Settings`.
3. Select `Manage User Roles`.
4. Select `Add new role` to create a new role, and fill in neccessary information up to the form.

### Assign the role to a user
5. From the `administration` page, click `Manage Users`.
6. Click `add single user`.
7. Create a user and assign it to the role you created in `Create an API user role` section.
8. You should receive an email with activation instructions. Follow them to activate your API user.
For more information visit [Create an API User page](https://knowledgecenter.zuora.com/Billing/Tenant_Management/A_Administrator_Settings/Manage_Users/Create_an_API_User)

### Create Client ID and Client Secret
9. From the `administration` page, click `Manage Users`.
10. Click on User Name of the target user.
11. Enter a client name and description and click `create`.
12. A pop-up will open with your Client ID and Client Secret.
    Make a note of your Client ID and Client Secret because they will never be shown again. You will need them to configure Airbyte Zuora Connector.
13. You're ready to set up Zuora connector in Airbyte, using created `Client ID` and `Client Secret`!


## Changelog

| Version | Date       | Pull Request | Subject |
| :------ | :--------  | :--------    | :------ |
| 0.1.0   | 2021-08-01 | [4661](https://github.com/airbytehq/airbyte/pull/4661) | Initial release of Native Zuora connector for Airbyte |

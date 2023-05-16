# Zuora

## Sync overview

The Zuora source supports both Full Refresh and Incremental syncs. You can choose if this connector will copy only the new or updated data, or all rows in the tables and columns you set up for replication, every time a sync is run.

Airbyte uses [REST API](https://www.zuora.com/developer/api-reference/#section/Introduction) to fetch data from Zuora. The REST API accepts [ZOQL \(Zuora Object Query Language\)](https://knowledgecenter.zuora.com/Central_Platform/Query/Export_ZOQL), a SQL-like language, to export the data.

### Output schema

This Source is capable of syncing:

- standard objects available in Zuora account
- custom objects manually added by user, available in Zuora Account
- custom fields in both standard and custom objects, available in Zuora Account

The discovering of Zuora Account objects schema may take a while, if you add the connection for the first time, and/or you need to refresh your list of available streams. Please take your time to wait and don't cancel this operation, usually it takes up to 5-10 min, depending on number of objects available in Zuora Account.

### Note

Some of the Zuora Objects may not be available for sync due to limitations of Zuora Supscription Plan, Permissions. For details refer to the [Availability of Data Source Objects](https://knowledgecenter.zuora.com/DC_Developers/M_Export_ZOQL) section in the Zuora documentation.

### Data type mapping

The following table provides the mapping of Zuora data types to Airbyte data types:

| Zuora Type | Airbyte Type              | Notes                                                                         |
| :--------- | :----------------------- | :---------------------------------------------------------------------------- |
| decimal    | number                   | float number                                                                  |
| float      | number                   | float number                                                                  |
| double     | number                   | float number                                                                  |
| int        | number                   | integer number                                                                |
| bigint     | number                   | long integer number                                                           |
| smallint   | number                   | short integer number                                                          |
| timestamp  | number                   | number representation of the unix timestamp                                   |
| date       | string                   |                                                                               |
| datetime   | string                   |                                                                               |
| picklist   | string                   |                                                                               |
| text       | string                   |                                                                               |
| varchar    | string                   |                                                                               |
| zoql       | object                   |                                                                               |
| binary     | object                   |                                                                               |
| json       | object                   |                                                                               |
| xml        | object                   |                                                                               |
| blob       | object                   |                                                                               |
| list       | array                    |                                                                               |
| array      | array                    |                                                                               |
| boolean    | boolean                  |                                                                               |
| bool       | boolean                  |                                                                               |
| Other      | string                   | Any other data type not listed in the table above will be treated as `string`. |

### Features

| Feature                            | Supported? (Yes/No) | Notes |
| :--------------------------------- | :------------------ | :---- |
| Full Refresh Overwrite Sync        | Yes                 |       |
| Full Refresh Append Sync           | Yes                 |       |
| Incremental - Append Sync          | Yes                 |       |
| Incremental - Append + Deduplication Sync | Yes          |       |
| Namespaces                         | No                  |       |

## Supported Environments for Zuora

| Environment | Supported? (Yes/No) | Notes                                              |
| ----------- | -------------------- | -------------------------------------------------- |
| Production  | Yes                  | Select from existing options while setup           |
| Sandbox     | Yes                  | Select from existing options while setup           |

## Supported Data Query options

| Option   | Supported? (Yes/No) | Notes                                                                                                                                                                                   |
| -------- | -------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| LIVE     | Yes                  | Run data queries against Zuora live transactional databases                                                                                                                             |
| UNLIMITED | Yes                  | Run data queries against an optimized, replicated database at 12 hours freshness for high volume extraction use cases (Early Adoption, additional access required, contact Zuora Support to request this feature enabled for your account beforehand.) |

## List of Supported Environments for Zuora

### Production

| Environment          | Endpoint          |
| -------------------- | ----------------- |
| US Production        | rest.zuora.com    |
| US Cloud Production  | rest.na.zuora.com |
| EU Production        | rest.eu.zuora.com |

### Sandbox

| Environment            | Endpoint                       |
| ---------------------- | ------------------------------ |
| US API Sandbox         | rest.apisandbox.zuora.com      |
| US API Sandbox         | rest.sandbox.na.zuora.com      |
| US Central Sandbox     | rest.test.zuora.com            |
| EU API Sandbox         | rest.sandbox.eu.zuora.com      |
| EU Central Sandbox     | rest.test.eu.zuora.com          |

### Other

| Environment            | Endpoint                       |
| ---------------------- | ------------------------------ |
| US Performance Test    | rest.pt1.zuora.com             |

For more information about available environments, please visit [this page](https://knowledgecenter.zuora.com/BB_Introducing_Z_Business/D_Zuora_Environments)

### Performance considerations

If you experience long times for sync operations, please consider:

- increasing the `window_in_days` parameter inside Zuora source configuration
- using a smaller date range by tuning the `start_date` parameter.

### Note

Usually, the very first sync operation for all of the objects inside a Zuora account takes up to 25-45-60 minutes, depending on the amount of data you have.

## Getting started

### Create an API user role

1. Log in to your Zuora account.
2. In the top right corner of the Zuora dashboard, select **Settings** > **Administration Settings**.
3. Select **Manage User Roles**.
4. Select **Add new role** to create a new role and fill in the necessary information in the form.

For more information, please visit the [Zuora Create an API User Role](https://knowledgecenter.zuora.com/Billing/Tenant_Management/A_Administrator_Settings/Manage_Users/Create_an_API_User) page.

### Assign the role to a user

1. From the **Administration** page, click **Manage Users**.
2. Click **Add Single User**.
3. Create a new user and assign them to the role you created in the **Create an API User Role** section.
4. You should receive an email with activation instructions. Follow them to activate your API user.

For more
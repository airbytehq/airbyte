# Zuora

## Sync overview

The Zuora source supports both Full Refresh and Incremental syncs. You can choose if this connector will copy only the new or updated data, or all rows in the tables and columns you set up for replication, every time a sync is run.

Airbyte uses [REST API](https://www.zuora.com/developer/api-reference/#section/Introduction) to fetch data from Zuora. The REST API accepts [ZOQL \(Zuora Object Query Language\)](https://knowledgecenter.zuora.com/Central_Platform/Query/Export_ZOQL), a SQL-like language, to export the data.

### Output schema

This Source is capable of syncing:

* standard objects available in Zuora account
* custom objects manually added by user, available in Zuora Account
* custom fields in both standard and custom objects, available in Zuora Account

The discovering of Zuora Account objects schema may take a while, if you add the connection for the first time, and/or you need to refresh your list of available streams. Please take your time to wait and don't cancel this operation, usually it takes up to 5-10 min, depending on the number of objects available in Zuora Account.

### Note:

Some of the Zuora Objects may not be available for sync due to limitations of Zuora Subscription Plan or Permissions. For details refer to the [Availability of Data Source Objects](https://knowledgecenter.zuora.com/DC_Developers/M_Export_ZOQL) section in the Zuora documentation.

### Data type mapping

_[Table explaining mapping from Zuora data types to Airbyte Data types]_

### Features

_[Table explaining supported features for Zuora integration]_

## Supported Environments for Zuora

_[Table explaining supported environments for Zuora]_

## Supported Data Query options

_[Table explaining supported data query options for Zuora]_

## List of Supported Environments for Zuora

### Production

_[Table explaining supported production environments for Zuora]_

### Sandbox

_[Table explaining supported sandbox environments for Zuora]_

### Other

_[Table explaining supported other environments for Zuora]_

For more information about available environments, please visit [this page](https://knowledgecenter.zuora.com/BB_Introducing_Z_Business/D_Zuora_Environments)

### Performance considerations

If you experience a long time for sync operation, please consider:

* increasing the `window_in_days` parameter inside the Zuora source configuration
* using a smaller date range by tuning the `start_date` parameter.

### Note

Usually, the very first sync operation for all of the objects inside a Zuora account takes up to 25-45-60 min. The more data you have, the more time you'll need.

## Getting started

### 1. Create an API user role

1. Log in to your `Zuora account`.
2. Navigate to `Settings` > `Administration Settings` in the top right corner of the Zuora dashboard.
3. Click on `Manage User Roles`.
4. Click on `Add new role` to create a new role, and fill in the necessary information in the form.

### 2. Assign the role to a user

1. Go to the `administration` page and click on `Manage Users`.
2. Click on `add single user`.
3. Create a user and assign it to the role you created in the `Create an API user role` section.
4. You should receive an email with activation instructions. Follow them to activate your API user.

   For more information, visit [Create an API User page](https://knowledgecenter.zuora.com/Billing/Tenant_Management/A_Administrator_Settings/Manage_Users/Create_an_API_User)

### 3. Create Client ID and Client Secret

1. Go to the `administration` page and click on `Manage Users`.
2. Click on the User Name of the target user.
3. Enter a client name and description, then click `create`.
4. A pop-up will open with your Client ID and Client Secret.

   Make a note of your Client ID and Client Secret because they will never be shown again. You will need them to configure the Airbyte Zuora Connector.

5. You're ready to set up the Zuora connector in Airbyte, using the created `Client ID` and `Client Secret`!

## Changelog

_[Table explaining versions and changes for Zuora connector]_

To configure the Zuora source connector in Airbyte, follow these steps:

1. In the Airbyte UI, click on **+ Add Source**.
2. Search for Zuora, click on it, and then click **Setup Source**.
3. Fill in the **Start Date**, **Query Window (in days)**, **Tenant Endpoint Location**, **Data Query Type**, **Client ID**, and **Client Secret** fields.

    - **Start Date** should be in the format of `YYYY-MM-DD`.
    - **Query Window (in days)** should be set according to the desired amount of days for each data chunk. The default value is 90 days.
    - **Tenant Endpoint Location** is where your Zuora tenant is located. Ensure that you select the correct location.
    - **Data Query Type** should be either `Live` or `Unlimited`.
    - **Client ID** and **Client Secret** are the credentials obtained in the previous steps.

4. Click **Test Connection** to ensure your credentials are correct along with the other connector settings.
5. Finally, click **Save Connection** to add the Zuora connector.
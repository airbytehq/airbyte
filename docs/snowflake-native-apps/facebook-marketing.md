# Facebook Marketing Connector

The Facebook Marketing Connector by Airbyte is a Snowflake Native Application that allows you to extract data from your Facebook Marketing account and load records into a Snowflake database of your choice.

:::info
The Snowflake Native Apps platform is new and rapidly evolving. The Facebook Marketing Connector by Airbyte is in _private preview_ and is subject to further development that may affect setup and configuration of the application. Please note that, at this time, only a [full table refresh](../understanding-airbyte/connections/full-refresh-overwrite.md) without deduplication is supported.  
:::

# Getting started

## Prerequisites
A Facebook Marketing account with permission to access data from accounts you want to sync.

## Installing the App

:::warning
Do not refresh the Apps page while the application is being installed. This may cause installation to fail.
:::

1. Log into your Snowflake account.
2. On the left sidebar, click `Marketplace`.
3. Search for `Facebook Marketing Connector` by Airbyte or navigate to https://app.snowflake.com/marketplace/listing/GZTYZ9BCRT8/airbyte-facebook-marketing-connector-by-airbyte
4. Click `Request`. This will send a request that we will manually service as soon as we can.
5. On the left sidebar, click `Apps`.
6. Under the `Recently Shared with You` section, you should see the `Facebook Marketing Connector by Airbyte`. Click `Get`.
7. Expand `Options`.
    1. You can rename the application or leave the default. This is how you will reference the application from a worksheet.
    2. Specify the warehouse that the application will be installed to.
8. Click `Get`.
9. Wait for the application to install. Once complete, the pop-up window should automatically close.

You should now see the Facebook Marketing Connector by Airbyte application under `Installed Apps`. You may need to refresh the page.

## Facebook Marketing Account
In order for the Facebook Marketing Connector by Airbyte to query Facebook's APIs, you will need an account with the right permissions. Please follow the [Facebook Marketing authentication guide](https://docs.airbyte.com/integrations/sources/facebook-marketing#for-airbyte-open-source-generate-an-access-token-and-request-a-rate-limit-increase) for further information.

## Snowflake Native App Authorizations

:::note
By default the app will be installed using the name `AIRBYTE_FACEBOOK_MARKETING`, but if you renamed the app during installation, you will have to use that name as a reference.
:::

1. Create the database where the app will access the authorization.
```
CREATE DATABASE airbyte_facebook_marketing_db;
USE airbyte_facebook_marketing_db;
```

2. The native app will validate the output database and create it if it does not exist. In order to do that, the app needs access to the database:
```
GRANT CREATE DATABASE ON ACCOUNT TO APPLICATION <app_name>;
```

3. You will need to allow outgoing network traffic based on the domain of the source. In the case of Facebook Marketing, simply run:
```
CREATE OR REPLACE NETWORK RULE facebook_marketing_apis_network_rule
  MODE = EGRESS
  TYPE = HOST_PORT
  VALUE_LIST = ('graph.facebook.com');
```

:::note  
As of 2023-09-13, the [Snowflake documentation](https://docs.snowflake.com/en/sql-reference/sql/create-external-access-integration) mentions that direct external access is a preview feature and that it is `available to all accounts on AWS` which might restrict the number of users able to use the connector.
:::

4. Once you have external access configured, you need define your authorization/authentication. Provide the credentials to the app as such:
```
CREATE OR REPLACE SECRET airbyte_app_secret
  TYPE = GENERIC_STRING
  SECRET_STRING = '{
    "access_token": "<access_token>"
  }';
```
... where `client_id`, `client_secret` and `refresh_token` are strings. For more information, see the [Facebook Marketing authentication guide](https://docs.airbyte.com/integrations/sources/facebook-marketing#for-airbyte-open-source-generate-an-access-token-and-request-a-rate-limit-increase).

5. Once the network rule and the secret are defined in Snowflake, you need to make them available to the app by using an external access integration.
```
CREATE OR REPLACE EXTERNAL ACCESS INTEGRATION airbyte_app_integration
  ALLOWED_NETWORK_RULES = (facebook_marketing_apis_network_rule)
  ALLOWED_AUTHENTICATION_SECRETS = (airbyte_app_secret)
  ENABLED = true;
```

6. Grant permission for the app to access the integration.
```
GRANT USAGE ON INTEGRATION airbyte_app_integration TO APPLICATION AIRBYTE_FACEBOOK_MARKETING;
```

7. Grant permissions for the app to access the database that houses the secret and read the secret.
```
GRANT USAGE ON DATABASE airbyte_facebook_marketing_db TO APPLICATION AIRBYTE_FACEBOOK_MARKETING;
GRANT USAGE ON SCHEMA public TO APPLICATION AIRBYTE_FACEBOOK_MARKETING;
GRANT READ ON SECRET airbyte_app_secret TO APPLICATION AIRBYTE_FACEBOOK_MARKETING;
```


## Configure a connection
Once this is all set up, you can now configure a connection. To do so, use the Streamlit app by going in the `Apps` section and selecting `AIRBYTE_FACEBOOK_MARKETING`. You will have to accept the Anaconda terms in order to use Streamlit. 

Once you have access to the app, select `New Connection` and fill the following fields:

--- 

`account_id`

The Facebook Ad account ID to use when pulling data from the Facebook Marketing API. The Ad account ID number is in the account dropdown menu or in your browser's address bar of your [Meta Ads Manager](https://adsmanager.facebook.com/adsmanager/).

--- 

`start_date`

UTC date in the format 2021-09-29T12:13:14Z. Any data before this date will not be replicated.

--- 

`end_date`

UTC date in the format 2021-09-29T12:13:14Z. Any data after this date will not be replicated.

---

`include_deleted`

The Facebook Marketing API does not have a concept of deleting records, and it maintains a record of Campaigns, Ads, and Ad Sets. Enabling this setting allows you to extract data that includes these objects that were archived or deleted from the Facebook platform.

---

`fetch_thumbnail_images`

When extracting Ad Creatives, retrieve the thumbnail_url and store it as thumbnail_data_url in each record.

---

`custom_insights`

Custom insights allow you to define ad statistic entries representing the performance of your campaigns against specific metrics. For more information about how to configure custom insights, please refer to the [Facebook Marketing documentation](https://docs.airbyte.com/integrations/sources/facebook-marketing#set-up-facebook-marketing-as-a-source-in-airbyte).

---

`page_size`

The number of records per page for paginated responses. The default is 100, but most users should not need to set this field except for unique use cases that require tuning the settings.

---

`insights_lookback_window`

The window in days to revisit data during syncing to capture updated conversion data from the API. Facebook allows for attribution windows of up to 28 days, during which time a conversion can be attributed to an ad. If you have set a custom attribution window in your Facebook account, please set the same value here.

---

`Output Database`

The database where the records will be saved. Snowflake's database [naming convention](https://docs.snowflake.com/en/sql-reference/identifiers-syntax) applies here.

---

`Output Schema`

The table where the schema will be saved. Snowflake's table [naming convention](https://docs.snowflake.com/en/sql-reference/identifiers-syntax) applies here. 

--- 

`Connection name`

How the connection will be referred in the Streamlit app.

--- 

`Replication Frequency`

How often records are fetched.

---

## Enabling Logging and Event Sharing for an Application
Sharing the logging and telemetry data of your installed application helps us improve the application and can allow us to better triage problems that your run into. To configure your application for logging and telemetry data please refer to the documentation for [Enabling Logging and Event Sharing](event-sharing.md).

## Run a sync
Once a connection is configured, go in `Connections List` and click on `Sync Now` for the connection you want to sync. Once the sync is complete, you should be able to validate that the records have been stored in `<your_database>.<your_schema>`

### Supported Streams
As of now, all supported streams perform a full refresh. Incremental syncs are not yet supported. Here are the list of supported streams:
* Activities
* Ad Account
* Ad Creatives
* Ad Insights
* Ad Sets
* Ads
* Campaigns
* Custom Audiences
* Custom Conversions

# Contact Us
snowflake-native-apps@airbyte.io

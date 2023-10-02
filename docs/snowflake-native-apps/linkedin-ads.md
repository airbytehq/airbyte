# LinkedIn Ads Connector

The LinkedIn Ads Connector by Airbyte is a Snowflake Native Application that allows you to extract data from your LinkedIn Ads account and load records into a Snowflake database of your choice.

:::info
The Snowflake Native Apps platform is new and rapidly evolving.  The LinkedIn Ads Connector by Airbyte is in _private preview_ and is subject to further development that may affect setup and configuration of the application. Please note that, at this time, only a full table refresh without dedupe is supported.  
:::

# Getting started

## Prerequisites
A LinkedIn Ads account with permission to access data from accounts you want to sync.

## Installing the App

:::warning
Do not refresh the Apps page while the application is being installed. This may cause installation to fail.
:::

1. Log into your Snowflake account.
2. On the left sidebar, click `Marketplace`.
3. Search for `Linkedin Ads Connector` by Airbyte or navigate to https://app.snowflake.com/marketplace/listing/GZTYZ9BCRSJ/airbyte-linkedin-ads-connector-by-airbyte
4. Click `Request`. This will send a request that we will manually service as soon as we can.
5. On the left sidebar, click `Apps`.
6. Under the `Recently Shared with You` section, you should see the `Linkedin Ads Connector by Airbyte`. Click `Get`.
7. Expand `Options`.
    1. You can rename the application or leave the default. This is how you will reference the application from a worksheet.
    2. Specify the warehouse that the application will be installed to.
8. Click `Get`.
9. Wait for the application to install. Once complete, the pop-up window should automatically close.

You should now see the LinkedIn Ads Connector by Airbyte application under `Installed Apps`. You may need to refresh the page.

## LinkedIn Ads Account
In order for the LinkedIn Ads Connector by Airbyte to query LinkedIn, you will need an account with the right permissions. Please follow the [LinkedIn Ads authentication guide](https://docs.airbyte.com/integrations/sources/linkedin-ads/#set-up-linkedin-ads-authentication-airbyte-open-source) for further information.

## Snowflake Native App Authorizations

:::note
By default the app will be installed using the name `AIRBYTE_LINKEDIN_ADS`, but if you renamed the app during installation, you will have to use that name as a reference.
:::

1. Create the database where the app will access the authorization. This database can be different from the database where the sync will output records.
```
CREATE DATABASE <database>;
USE <database>;
```

2. The native app will validate the output database and create it if it does not exist. In order to do that, the app needs access to the database:
```
GRANT CREATE DATABASE ON ACCOUNT TO APPLICATION <app_name>;
```

3. You will need to allow outgoing network traffic based on the domain of the source. In the case of LinkedIn Ads, simply run:
```
CREATE OR REPLACE NETWORK RULE linkedin_apis_network_rule
  MODE = EGRESS
  TYPE = HOST_PORT
  VALUE_LIST = ('api.linkedin.com', 'www.linkedin.com', 'linkedin.com');
```

:::note  
As of 2023-09-13, the [Snowflake documentation](https://docs.snowflake.com/en/sql-reference/sql/create-external-access-integration) mentions that direct external access is a preview feature and that it is `available to all accounts on AWS` which might restrict the number of users able to use the connector.
:::

4. Once you have external access configured, you need define your authorization/authentication. Provide the credentials to the app as such:
```
CREATE OR REPLACE SECRET integration_linkedin_ads_oauth
  TYPE = GENERIC_STRING
  SECRET_STRING = '{
    "auth_method": "oAuth2.0",
    "client_id": <client_id>,
    "client_secret": <client_secret>,
    "refresh_token": <refresh_token>
  }';
```
... where `client_id`, `client_secret` and `refresh_token` are strings. For more information, see the [LinkedIn Ads authentication guide](https://docs.airbyte.com/integrations/sources/linkedin-ads/#set-up-linkedin-ads-authentication-airbyte-open-source).

5. Once the network rule and the secret are defined in Snowflake, you need to make them available to the app by using an external access integration.
```
CREATE OR REPLACE EXTERNAL ACCESS INTEGRATION integration_linkedin_ads
  ALLOWED_NETWORK_RULES = (linkedin_apis_network_rule)
  ALLOWED_AUTHENTICATION_SECRETS = (integration_linkedin_ads_oauth)
  ENABLED = true;
```

6. Grant permission for the app to access the integration.
```
GRANT USAGE ON INTEGRATION integration_linkedin_ads TO APPLICATION AIRBYTE_LINKEDIN_ADS;
```

7. Grant permissions for the app to access the database that houses the secret and read the secret.
```
GRANT USAGE ON DATABASE <your_database> TO APPLICATION AIRBYTE_LINKEDIN_ADS;
GRANT USAGE ON SCHEMA <your_schema> TO APPLICATION AIRBYTE_LINKEDIN_ADS;
GRANT READ ON SECRET integration_linkedin_ads_oauth TO APPLICATION AIRBYTE_LINKEDIN_ADS;
```


## Configure a connection
Once this is all set up, you can now configure a connection. To do so, use the Streamlit app by going in the `Apps` section and selecting `AIRBYTE_LINKEDIN_ADS`. You will have to accept the Anaconda terms in order to use Streamlit. 

![](./linkedin-ads-ui.gif)

Once you have access to the app, select `New Connection` and fill the following fields:

--- 

`Secret` 

The name of the secret prefixed by which database and schema. Based on the previous steps: `<database>.<your_schema>.integration_linkedin_ads_oauth`.

---

`External Access Integration`

Name of the Snowflake integration where the secret and network rules are configured. Based on the previous steps: `integration_linkedin_ads`.

--- 

`start_date`

UTC date in the format 2020-09-17. Any data before this date will not be replicated. 

---

`account_ids`

Leave empty, if you want to pull the data from all associated accounts. To specify individual account IDs to pull data from, separate them by a space. See the [LinkedIn Ads docs](https://www.linkedin.com/help/linkedin/answer/a424270/find-linkedin-ads-account-details) for more info.

---

`Output Database`

The database where the records will be saved. Snowflake's database naming restriction applies here.

---

`Output Schema`

The table where the schema will be saved. Snowflake's table naming restriction applies here. 

--- 

`Connection name`

How the connection will be referred in the Streamlit app.

--- 

`Replication Frequency`

How often records are fetched.

---

## Run a sync
Once a connection is configured, go in `Connections List` and click on `Sync Now` for the connection you want to sync. Once the sync is complete, you should be able to validate that the records have been stored in `<your_database>.<your_schema>`

### Supported Streams
As of now, all supported streams perform a full refresh. Incremental syncs are not yet supported. Here are the list of supported streams:
* Accounts
* Account Users
* Ad Analytics by Campaign
* Ad Analytics by Creative
* Campaigns
* Campaign Groups
* Creatives

# Contact Us
snowflake-native-apps@airbyte.io

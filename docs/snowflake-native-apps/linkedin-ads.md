The LINKEDIN_ADS_TEST Snowflake Native Application allows you to sync records from LinkedIn Ads to Snowflake all within Snowflake.

# Getting started

## Onboarding steps  
Even though you can request that app in the Snowflake Marketplace, this will not grant you access as it is in private preview. 
If you have been granted access, you should be able to add the application to your workspace by clicking on `GET` in the `Apps` section.

## LinkedIn Account
In order for the Snowflake Native App to query LinkedIn, you will need an account with the right permissions. Please follow [the LinkedIn Ads authentication guide](https://docs.airbyte.com/integrations/sources/linkedin-ads/#set-up-linkedin-ads-authentication-airbyte-open-source) for further information.

## Snowflake Native App Authorizations
1. Create the database where the app will access the authorization. This database can be different from the database where the sync will output the records.
```
CREATE DATABASE <database>;
USE <database>;
```
2. The native app will validate the output database and create it if it does not exist. In order to do that, the app needs access to the database:
```
GRANT CREATE DATABASE ON ACCOUNT TO APPLICATION LINKEDIN_ADS_TEST;
```
3. We also need to allow outgoing network traffic based on the domain of the source. In the case of LinkedIn Ads, simply run:
```
CREATE OR REPLACE NETWORK RULE linkedin_apis_network_rule
  MODE = EGRESS
  TYPE = HOST_PORT
  VALUE_LIST = ('api.linkedin.com', 'www.linkedin.com', 'linkedin.com');
```

> **Note**  
> As of 2023-09-13, the [Snowflake documentation](https://docs.snowflake.com/en/sql-reference/sql/create-network-rule) mentions this is a preview feature and that it is `available to all accounts on AWS` which might restrict the number of users able to use the connector.

4. Once we have access, we need authorization/authentication. Provide the credentials to the app as such:
```
CREATE OR REPLACE SECRET integration_tests_linkedin_oauth
  TYPE = GENERIC_STRING
  SECRET_STRING = '{
    "auth_method": "oAuth2.0",
    "client_id": <client_id>,
    "client_secret": <client_secret>,
    "refresh_token": <refresh_token>
  }';
```
... where `client_id`, `client_secret` and `refresh_token` are strings. For more information, see [the LinkedIn Ads authentication guide](https://docs.airbyte.com/integrations/sources/linkedin-ads/#set-up-linkedin-ads-authentication-airbyte-open-source).
5. Once the network rule and the secret is in Snowflake, we just need to make them available to the app.
```
-- create external access integration
CREATE OR REPLACE EXTERNAL ACCESS INTEGRATION LINKEDIN_ADS_TEST
  ALLOWED_NETWORK_RULES = (linkedin_apis_network_rule)
  ALLOWED_AUTHENTICATION_SECRETS = (integration_tests_linkedin_oauth)
  ENABLED = true;
  
-- grant permissions to access the integration
GRANT USAGE ON INTEGRATION integration_tests_linkedin_integration TO APPLICATION LINKEDIN_ADS_TEST;
-- grant access the the secret
GRANT USAGE ON DATABASE <your database> TO APPLICATION LINKEDIN_ADS_TEST;
GRANT USAGE ON SCHEMA public TO APPLICATION LINKEDIN_ADS_TEST;
GRANT READ ON SECRET integration_tests_linkedin_oauth TO APPLICATION LINKEDIN_ADS_TEST;
```

## Configure a connection
Once this is all set up, you can now configure a connection. To do so, use the Streamlit app by going in the `Apps` section and selecting `LINKEDIN_ADS_TEST`. You will have to accept the Anaconda terms in order to use Streamlit.
Once you have access to the app, select `New Connection` and fill the fields as such:
* Secret: `<database>.public.integration_tests_linkedin_oauth`
* External Access Integration: `integration_tests_linkedin_integration`
* start_date: UTC date in the format 2020-09-17. Any data before this date will not be replicated.
* account_ids: Specify the account IDs separated by a space, to pull the data from. Leave empty, if you want to pull the data from all associated accounts. See the [LinkedIn Ads docs](https://www.linkedin.com/help/linkedin/answer/a424270/find-linkedin-ads-account-details) for more info.
* Output Database: The database where the records will be saved. Snowflake's database naming restriction applies here.
* Output Schema: The table where the schema will be saved. Snowflake's table naming restriction applies here. 
* Connection name: How the connection will be referred in the Streamlit app
* Replication Frequency: How often do the records will be fetched

## Run a sync
Once a connection is configured, go in `Connections List` and click on `Sync Now` for the connection you want to sync. Under the hood, this simply calls the procedure `call LINKEDIN_ADS_TEST.APP.SYNC(<connection ID>);`. Once the sync is done, you should be able to validate that the records are in `<database>.<schema>`

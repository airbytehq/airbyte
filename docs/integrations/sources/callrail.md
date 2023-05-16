# CallRail

## Overview

The CallRail source supports Full Refresh and Incremental syncs to pull data from the following core Streams:

* [Calls](https://apidocs.callrail.com/#calls)
* [Companies](https://apidocs.callrail.com/#companies)
* [Text Messages](https://apidocs.callrail.com/#text-messages)
* [Users](https://apidocs.callrail.com/#users)


## Getting started

### Requirements

Before setting up the CallRail Source connector, ensure you have the following requirements ready:

* A CallRail account
* A CallRail API Token


### Obtaining a CallRail API Token

To obtain your CallRail API Token, follow these steps:

1. Log in to your CallRail account.
2. Click on "Settings" on the top right drop-down menu.
3. Click on "API" in the navigation menu on the left.

   ![](https://raw.githubusercontent.com/airbytehq/airbyte/master/docs/assets/img/sources/callrail/callrail_get_api_token.png)

4. If you have not already generated an API token, click the "Generate Token" button to generate one.

   ![](https://raw.githubusercontent.com/airbytehq/airbyte/master/docs/assets/img/sources/callrail/callrail_generate_api_token.png)

5. Copy the generated API Token.

   ![](https://raw.githubusercontent.com/airbytehq/airbyte/master/docs/assets/img/sources/callrail/callrail_copy_api_token.png)


### Adding CallRail Source Connector in Airbyte

Enter the following parameter values to set up the CallRail Source connector:

* `api_key`: Enter the CallRail API Token generated in the previous steps.
* `account_id`: Enter your CallRail Account ID. You can find it in the URL when you are signed into CallRail, the format is https://app.callrail.com/a/[account_id]/calls.
* `start_date`: Enter the date you want to start getting data using the format `YYYY-MM-DD`.

   ![](https://raw.githubusercontent.com/airbytehq/airbyte/master/docs/assets/img/sources/callrail/callrail_add_connection.png)

After entering the correct information, click on "Test Connection" to test if the connection is set up correctly.

Congratulations! You have successfully set up the CallRail Source connector in Airbyte.
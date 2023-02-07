## Prerequisite

* Access to a Notion workspace
​
## Setup guide

1. Choose the method of authentication:
   * To use OAuth2.0 authorization, click **Authenticate your Notion account**.
   * If you select Access Token, create a new integration in our [full documentation](https://docs.airbyte.com/integrations/sources/notion)
2. (Optional) Enter the Start Date in `YYYY-MM-DDTHH:mm:ss.SSSZ`. All data generated after this date will be replicated. If this field is blank, Airbyte will replicate all data.
3. Click **Set up source**.
​
For detailed information on supported sync modes, supported streams, performance considerations, refer to the full documentation for [Notion](https://docs.airbyte.com/integrations/sources/notion).
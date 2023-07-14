## Prerequisite

* Access to a Notion workspace
​
## Setup guide

1. Enter a **Source name** to help you identify this source in Airbyte.
2. Choose the method of authentication:

<!-- env:cloud -->
:::note
We highly recommend using OAuth2.0 authorization to connect to Notion. This method is more secure and significantly simplifies the setup process. If you use OAuth2.0 authorization, you do _not_ need to create a new integration in Notion. Instead, you can authenticate your Notion account directly in Airbyte Cloud.
:::

* To use OAuth2.0 authorization, select **OAuth2.0** from the dropdown menu, then click **Authenticate your Notion account**. When the popup appears, click **Select pages**. Check the pages you want to give Airbyte access to, and click **Allow access**.
* If you select Access Token, create a new integration in our [full documentation](https://docs.airbyte.com/integrations/sources/notion)
<!-- /env:cloud -->

<!-- env:oss -->
* To use OAuth2.0 authorization, click **
<!-- /env:oss -->

3. Enter the **Start Date** using the provided datepicker, or by programmatically entering a UTC timestamp in the format: `YYYY-MM-DDTHH:mm:ss.SSSZ`. All data generated after this date will be replicated.
4. Click **Set up source** and wait for the tests to complete.
​
For detailed information on supported sync modes, supported streams, performance considerations, refer to the [full documentation](https://docs.airbyte.com/integrations/sources/notion).

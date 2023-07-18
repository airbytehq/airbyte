## Prerequisite

* Access to a Notion workspace
​
## Setup guide

1. Enter a **Source name** to help you identify this source in Airbyte.
2. Choose the method of authentication:

<!-- env:cloud -->
:::note
We highly recommend using OAuth2.0 authorization to connect to Notion, as this method significantly simplifies the setup process. If you use OAuth2.0 authorization, you do _not_ need to create and configure a new integration in Notion. Instead, you can authenticate your Notion account directly in Airbyte Cloud.
:::

- **OAuth2.0** (Recommended): Click **Authenticate your Notion account**. When the popup appears, click **Select pages**. Check the pages you want to give Airbyte access to, and click **Allow access**.
- **Access Token**: Copy and paste the Access Token found in the **Secrets** tab of your Notion integration's page. For more information on how to create and configure an integration in Notion, refer to our 
[full documentation](https://docs.airbyte.io/integrations/sources/notion#setup-guide).
<!-- /env:cloud -->

<!-- env:oss -->
- **Access Token**: Copy and paste the Access Token found in the **Secrets** tab of your Notion integration's page.
- **OAuth2.0**: Copy and paste the Client ID, Client Secret and Access Token you acquired.

To obtain the necessary authorization credentials, you need to create and configure an integration in Notion. For more information on how to create and configure an integration in Notion, refer to our
[full documentation](https://docs.airbyte.io/integrations/sources/notion#setup-guide).
<!-- /env:oss -->

3. Enter the **Start Date** using the provided datepicker, or by programmatically entering a UTC date and time in the format: `YYYY-MM-DDTHH:mm:ss.SSSZ`. All data generated after this date will be replicated.
4. Click **Set up source** and wait for the tests to complete.
​

For detailed information on supported sync modes, supported streams, performance considerations, refer to the 
[full documentation for Notion](https://docs.airbyte.com/integrations/sources/notion).

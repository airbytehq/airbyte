## Prerequisite

* Access to your HubSpot account

## Setup guide

1. For **Start date**, enter the date in `YYYY-MM-DDTHH:mm:ssZ` format. The data added on and after this date will be replicated. If this field is blank, Airbyte will replicate all data.
2. You can use OAuth or an API key to authenticate your HubSpot account. We recommend using OAuth for Airbyte Cloud and an API key for Airbyte Open Source.
   * To authenticate using OAuth for Airbyte Cloud, ensure you have set the appropriate scopes for HubSpot and then click **Authenticate your HubSpot account** to sign in with HubSpot and authorize your account.
   * To authenticate using an API key for Airbyte Open Source, select **API key** from the Authentication dropdown and enter the [API key](https://knowledge.hubspot.com/integrations/how-do-i-get-my-hubspot-api-key) for your HubSpot account. Check the [performance considerations](https://docs.airbyte.com/integrations/sources/hubspot/#performance-considerations) before using an API key.
3. Click Set up source.

For detailed information on supported sync modes, supported streams, performance considerations, refer to the full documentation for [Hubspot](https://docs.airbyte.com/integrations/sources/hubspot/).
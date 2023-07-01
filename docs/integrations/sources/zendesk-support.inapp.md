## Prerequisites

- Locate your Zendesk subdomain found in your account URL. For example, if your account URL is `https://{MY_SUBDOMAIN}.zendesk.com/`, then `MY_SUBDOMAIN` is your subdomain.
- (For Airbyte Open Source) Find the email address associated with your Zendesk account. Also, generate an [API token](https://support.zendesk.com/hc/en-us/articles/4408889192858-Generating-a-new-API-token) for the account.

## Setup Guide

1. Enter a name for your source.
2. You can use OAuth or an API key to authenticate your Zendesk Support account. We recommend using OAuth for Airbyte Cloud and an API key for Airbyte Open Source.
   - To authenticate using OAuth for Airbyte Cloud, click **Authenticate your Zendesk Support account** to sign in with Zendesk Support and authorize your account.
   - To authenticate using an API key for Airbyte Open Source, select **API key** from the Authentication dropdown and enter your API key from the prerequisites. Enter the **Email** associated with your Zendesk Support account.
3. For **Start date**, enter the date in `YYYY-MM-DDTHH:mm:ssZ` format. The data added on and after this date will be replicated. If this field is blank, Airbyte will replicate all data.
4. For **Subdomain**, enter your Zendesk subdomain from the prerequisites.


5. Click **Set up source**.

For detailed information on supported sync modes, supported streams, performance considerations, refer to the full documentation for [Zendesk Support](https://docs.airbyte.com/integrations/sources/zendesk-support).

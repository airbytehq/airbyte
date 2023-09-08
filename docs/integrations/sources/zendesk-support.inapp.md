## Prerequisites

- A Zendesk account with an Administrator role.

## Setup Guide

<!-- env:oss -->

For **Airbyte Open Source** users, we recommend using an API token to authenticate your Zendesk account. You can follow the steps in our [full documentation](https://docs.airbyte.com/integrations/sources/zendesk-support#setup-guide) to generate this token.

<!-- /env:oss -->

1. For **Source name**, enter a name to help you identify this source.
2. You can use OAuth or an API token to authenticate your Zendesk account. We recommend using OAuth for Airbyte Cloud and an API token for Airbyte Open Source.

   <!-- env:cloud -->
   - **For Airbyte Cloud:** To authenticate using OAuth, select **OAuth2.0** from the Authentication dropdown, then click **Authenticate your Zendesk Support account** to sign in with Zendesk and authorize your account.
   <!-- /env:cloud -->
   <!-- env:oss -->
   - **For Airbyte Open Source**: To authenticate using an API token, select **API Token** from the Authentication dropdown and enter the [token you generated](https://docs.airbyte.com/integrations/sources/zendesk-support#setup-guide), as well as the email address associated with your Zendesk account.
   <!-- /env:oss -->

3. For **Start Date**, use the provided datepicker or enter a UTC date and time programmatically in the format `YYYY-MM-DDTHH:mm:ssZ`. The data added on and after this date will be replicated.
4. For **Subdomain**, enter your Zendesk subdomain. This is the subdomain found in your account URL. For example, if your account URL is `https://MY_SUBDOMAIN.zendesk.com/`, then `MY_SUBDOMAIN` is your subdomain.
5. Click **Set up source** and wait for the tests to complete.

For detailed information on supported sync modes, supported streams and performance considerations, refer to the [full documentation for Zendesk Support](https://docs.airbyte.com/integrations/sources/zendesk-support).

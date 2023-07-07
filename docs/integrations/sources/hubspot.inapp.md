## Prerequisites

- HubSpot Account
- **For Airbyte Open Source**: Private App with Access Token

### Authentication method
You can use OAuth or a Private App to authenticate your HubSpot account.  For Airbyte Cloud users, we highly recommend you use OAuth rather than Private App authentication, as it significantly simplifies the setup process.

For more information on which authentication method to choose and the required setup steps, see our full
[Hubspot documentation](https://docs.airbyte.com/integrations/sources/hubspot/).

### Scopes Required (for Private App and Open Source OAuth)
Unless you are authenticating via OAuth on **Airbyte Cloud**, you must manually configure scopes to ensure Airbyte can sync all available data. To see a breakdown of the specific scopes each stream uses, see our full [Hubspot documentation](https://docs.airbyte.com/integrations/sources/hubspot/).

* `content`
* `forms`
* `tickets`
* `automation`
* `e-commerce`
* `sales-email-read`
* `crm.objects.companies.read`
* `crm.schemas.companies.read`
* `crm.objects.lists.read`
* `crm.objects.contacts.read`
* `crm.objects.deals.read`
* `crm.schemas.deals.read`
* `crm.objects.goals.read`
* `crm.objects.owners.read`
* `crm.objects.custom.read`

## Setup guide

1. Log in to your [Airbyte Cloud](https://cloud.airbyte.com/workspaces) or Airbyte Open Source account.
2. From the Airbyte UI, click **Sources**, then click on **+ New Source** and select **HubSpot** from the list of available sources.
3. Enter a **Source name** of your choosing.
4. From the **Authentication** dropdown, select your chosen authentication method:

<!-- env:cloud -->
#### For Airbyte Cloud users:
- To authenticate using OAuth, select **OAuth** and click **Authenticate your HubSpot account** to sign in with HubSpot and authorize your account.
- To authenticate using a Private App, select **Private App** and enter the Access Token for your HubSpot account.
<!-- /env:cloud -->

<!-- env:oss -->
#### For Airbyte Open Source users:
- To authenticate using OAuth, select **OAuth** and enter your Client ID, Client Secret, and Refresh Token.
- To authenticate using a Private App, select **Private App** and enter the Access Token for your HubSpot account.
<!-- /env:oss -->

5. For **Start date**, use the provided datepicker or enter the date programmatically in the following format:
`yyyy-mm-ddThh:mm:ssZ`. The data added on and after this date will be replicated. If this field is blank, Airbyte will replicate all data.
6. Click **Set up source** and wait for the tests to complete.

## Supported Objects
Airbyte supports syncing standard and custom CRM objects. Custom CRM objects will appear as streams available for sync, alongside the standard objects.

For detailed information on supported sync modes, supported streams, performance considerations, refer to the full documentation for [Hubspot](https://docs.airbyte.com/integrations/sources/hubspot/).

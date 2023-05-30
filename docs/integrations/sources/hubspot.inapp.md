## Prerequisite

* Access to your HubSpot account

## Setup guide

1. You can use OAuth or a Private App to authenticate your HubSpot account. We recommend using OAuth for Airbyte Cloud.
   * To authenticate using OAuth for Airbyte Cloud, ensure your user has the appropriate scopes for HubSpot and then click **Authenticate your HubSpot account** to sign in with HubSpot and authorize your account.
   * To authenticate using a Private App, navigate to **Settings** and click **Private Apps** under Account Setup. Create a new private app and add the appropriate scopes to your private app.
2. (Optional) For **Start date**, enter the date in `YYYY-MM-DDTHH:mm:ssZ` format. The data added on and after this date will be replicated. If this field is blank, Airbyte will replicate all data.
3. Click Set up source.

## Scopes Required (for Private App)
Add the following scopes to your private app to ensure Airbyte can sync all available data. To see a breakdown of the specific scopes each stream uses, see our full [Hubspot documentation](https://docs.airbyte.com/integrations/sources/hubspot/).

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

## Supported Objects
Airbyte supports syncing standard and custom CRM objects. Custom CRM objects will appear as streams available for sync, alongside the standard objects.


For detailed information on supported sync modes, supported streams, performance considerations, refer to the full documentation for [Hubspot](https://docs.airbyte.com/integrations/sources/hubspot/).
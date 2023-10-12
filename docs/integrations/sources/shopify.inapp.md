## Prerequisites

* An active [Shopify store](https://www.shopify.com).
* If you are syncing data from a store that you do not own, you will need to [request access to your client's store](https://help.shopify.com/en/partners/dashboard/managing-stores/request-access#request-access) (not required for account owners).

:::note
For existing Shopify sources, if you previously used the **API Password** authentication method, please switch to **OAuth2.0**, as the API Password will be deprecated shortly. If you prefer to continue using **API Password**, the option will remain available in **Airbyte Open Source**.
:::

## Setup guide

### Connect using OAuth2.0

1. Click **Authenticate your Shopify account**.
2. Click **Install** to install the Airbyte application.
3. Log in to your account, if you are not already logged in.
4. Select the store you want to sync and review the consent.
5. Click **Install** to finish the installation.
6. The **Shopify Store** field will be automatically filled based on the store you selected. Confirm the value is accurate.
7. (Optional) You may set a **Replication Start Date** as the starting point for your data replication. Any data created before this date will not be synced. Please note that this defaults to January 1st, 2020.
8. Click **Set up source** and wait for the connection test to complete.

For detailed information on supported sync modes, supported streams and performance considerations, refer to the [full documentation for Shopify](https://docs.airbyte.com/integrations/sources/shopify).

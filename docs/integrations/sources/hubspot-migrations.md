# HubSpot Migration Guide

## Upgrading to 2.0.0

Note: this change is only breaking if you are using PropertyHistory stream

With this update, we have access to historical property changes for Deals and Companies, just like we have it for Contacts. That is why Property History stream was renamed to Contacts Property History and two new streams were added: Deals Property History and Companies Property History.
This is a breaking change because Property History by fact was replaced with Contacts Property History, so please follow the instructions below to migrate to version 2.0.0:

1. Select **Connections** in the main navbar, then find and select the connection(s) affected by the update.
2. Select the **Replication** tab, then select **Refresh source schema**. Any detected schema changes will be listed for your review. Select **OK** when you are ready to proceed.
3. Scroll to the bottom of the page and select **Save changes**. You will be prompted to reset your data (depending on destination type you may not be prompted). Ensure the **Reset affected streams** option is checked , and select **Save connection**. This will reset the data in your destination and initiate a fresh sync.

For more information on resetting your data in Airbyte, see [this page](https://docs.airbyte.com/operator-guides/reset).

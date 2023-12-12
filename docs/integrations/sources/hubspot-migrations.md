# HubSpot Migration Guide

## Upgrading to 2.0.0

Note: this change is only breaking if you are using the PropertyHistory stream.

With this update, you can now access historical property changes for Deals and Companies, in addition to Contacts. Property History stream has been renamed to Contacts Property History (since it historically contained historical property changes from Contacts) and two new streams were added: Deals Property History and Companies Property History.
This is a breaking change because Property History has been replaced with Contacts Property History, so please follow the instructions below to migrate to version 2.0.0:

1. Select **Connections** in the main navbar.
1.1 Select the connection(s) affected by the update.
2. Select the **Replication** tab.
2.1 Select **Refresh source schema**.
        ```note
        Any detected schema changes will be listed for your review.
        ```
2.2 Select **OK**.
3. Select **Save changes** at the bottom of the page.
3.1 Ensure the **Reset affected streams** option is checked.
        ```note
        Depending on destination type you may not be prompted to reset your data
        ```
4. Select **Save connection**.
        ```note
        This will reset the data in your destination and initiate a fresh sync.
        ```

For more information on resetting your data in Airbyte, see [this page](https://docs.airbyte.com/operator-guides/reset).

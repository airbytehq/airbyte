# Weatherstack Migration Guide

## Upgrading to 1.0.0

Version 1.0.0 introduces changes to the connection configuration. The `is_paid_account` config input is removed and streams unavailable to unpaid accounts will simply be empty when read.

Due to this upgrade, no synced streams were affected. However, for unpaid accounts, the following streams which were initially hidden will now appear but with empty records since the API only makes them available for paid accounts.

1. historical
2. location_lookup

## Migration Steps

### Refresh source schemas and reset data

1. Select **Connections** in the main nav bar.
    1. Select the connection(s) affected by the update.
2. Select the **Replication** tab.
    1. Select **Refresh source schema**.
    2. Select **OK**.
        > [!NOTE]  
        > Any detected schema changes will be listed for your review.
3. Select **Save changes** at the bottom of the page.
    1. Ensure the **Reset affected streams** option is checked.
        > [!NOTE]  
        > Depending on destination type you may not be prompted to reset your data.
4. Select **Save connection**. 
    > [!NOTE]  
    > This will reset the data in your destination and initiate a fresh sync.

For more information on resetting your data in Airbyte, see [this page](https://docs.airbyte.com/operator-guides/reset).

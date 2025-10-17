# YouTube Analytics Migration Guide

## Upgrading to 1.0.0

The YouTube Analytics Bulk Reports API made changes one of which is  create new report versions for each report that includes views, which is the majority of the reports. Each affected report's version has incremented by one, such as version a2 to version a3. See [here](https://developers.google.com/youtube/reporting/revision_history#june-24,-2025) for more details.

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

<MigrationGuide />

# Looker Migration Guide

## Upgrading to 1.0.0

Version 1.0.0 introduces changes to the connection configuration which has been upgraded to the API v4.0 from v3.1. Due to this upgrade, the following streams were affected;

1. homepages, homepage_items and homepage_sections streams are replaced with boards, board_items and board_sections streams respectively.
2. spaces and space_ancestors streams have been removed in favour of folders and folder_ancestors streams
3. lookml_dashboards stream has been removed in favour of dashboards stream

In addtion to affected streams, the schemas of the streams are expected to change.

For details about the API migration, check out [here](https://cloud.google.com/looker/docs/api-3x-deprecation)

## Migration Steps

### Refresh affected schemas and reset data

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

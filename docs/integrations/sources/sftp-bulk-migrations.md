# SFTP Bulk Migration Guide

## Upgrading to 1.0.0
This release upgrades the SFTP Bulk connector to file-based CDK which causes the following changes:

- Configuration changes
- Stream changes

Users should:

- Reconfigure the source
- Refresh the source schema
- Reset affected streams after upgrading to ensure uninterrupted syncs.


### Refresh affected schemas and reset data

1. Select **Connections** in the main navbar.
    1. Select the connection(s) affected by the update.
2. Select the **Replication** tab.
    1. Select **Refresh source schema**.
    2. Select **OK**.
```note
Any detected schema changes will be listed for your review.
```
3. Select **Save changes** at the bottom of the page.
    1. Ensure the **Reset affected streams** option is checked.
```note
Depending on destination type you may not be prompted to reset your data.
```
4. Select **Save connection**. 
```note
This will reset the data in your destination and initiate a fresh sync.
```

For more information on resetting your data in Airbyte, see [this page](https://docs.airbyte.com/operator-guides/reset).
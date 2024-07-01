# Snapchat Marketing Migration Guide

## Upgrading to 1.0.0

We're continuously striving to enhance the quality and reliability of our connectors at Airbyte.
As part of our commitment to delivering exceptional service, we are transitioning Snapchat Marketing source from 
the Python Connector Development Kit (CDK) to our innovative low-code framework. This is part of a strategic move 
to streamline many processes across connectors, bolstering maintainability and freeing us to focus more of our efforts 
on improving the performance and features of our evolving platform and growing catalog. However, due to differences 
between the Python and low-code CDKs, this migration constitutes a breaking change.

To gracefully handle these changes for your existing connections, we highly recommend resetting your data before resuming your data syncs with the new version.

### Migration Steps

1. Select **Connections** in the main navbar.
   1. Select the connection(s) affected by the update.
2. Select the **Schema** tab.
3. Uncheck all streams except the affected ones.
4. Select **Save changes** at the bottom of the page.
5. Select the **Settings** tab.
6. Press the **Clear your data** button.
7. Return to the **Schema** tab.
8. Check all your streams.
9. Select **Sync now** to sync your data

For more information on resetting your data in Airbyte, see [this page](/operator-guides/clear).

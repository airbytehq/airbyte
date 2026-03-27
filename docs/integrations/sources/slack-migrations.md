# Slack Migration Guide

## Upgrading to 3.0.0

This update fixes a bug that prevented incremental syncs from progressing for some connections containing the `threads` stream.

- **If you sync the `threads` stream in Full Refresh mode**: you can upgrade directly to v3.0.0 and skip the migration steps.  
- **If you sync the `threads` stream in Incremental mode**: check the criteria below. If either applies, follow the migration steps.  

### Check before upgrading

1. **Threads stream state** — if the state is empty, follow the migration steps.  
2. **Destination records** — if duplicate records exist for the Threads stream, follow the migration steps.  

### How to check connection state for the Threads stream

1. Go to the connection using source Slack.
2. Select the **Settings** tab.
3. Under **Connection state**, find the JSON object with `"name": "threads"` in `streamDescriptor` and check its `streamState`.

If the state looks similar to the following example, follow the migration steps:

```json
{
    "streamDescriptor": {
      "name": "threads"
    },
    "streamState": {
      "__ab_no_cursor_state_message": true
    }
}
```

### Migration steps

To clear your data for the `Threads` stream:

1. Select **Connections** in the main nav bar.
   1. Select the connection(s) affected by the update.
2. Select the **Status** tab.
   1. In the **Enabled streams** list, click the three dots on the right side of the `Threads` and select **Clear Data**.

After the clear succeeds, trigger a sync by clicking **Sync Now**. For more information on clearing your data in Airbyte, see [this page](/platform/operator-guides/clear).

## Upgrading to 2.0.0

Due to changes in the Slack API [Terms of Service](https://api.slack.com/changelog/2025-05-terms-rate-limit-update-and-faq), the connector migrated to a new Marketplace OAuth application. Users must re-authenticate their source with the new application to refresh their access token. This does not apply if you use an API token, are on Airbyte Open Source, or supply your own Slack OAuth application credentials.

### Migration steps

1. In the Airbyte application, navigate to your Slack source.
2. Under **Authentication mechanism**, click **Authenticate your Slack account**.
3. Follow the instructions in the pop-up window and click **Allow** to grant permissions to access your workspace.

## Upgrading to 1.0.0

This version migrated the Slack source connector from the Python CDK to the low-code declarative framework. Due to differences in how state is managed for incremental substreams, this is a breaking change for the `Channel Messages` stream. The new state format uses a more structured approach for partition-level state management.

### Migration steps

You must clear data for the `Channel Messages` stream to continue syncing successfully:

1. Select **Connections** in the main nav bar.
   1. Select the connection(s) affected by the update.
2. Select the **Status** tab.
   1. In the **Enabled streams** list, click the three dots on the right side of the `Channel Messages` and select **Clear Data**.

After the clear succeeds, trigger a sync by clicking **Sync Now**. For more information on clearing your data in Airbyte, see [this page](/platform/operator-guides/clear).

# Slack Migration Guide

## Upgrading to 3.0.0

Due to a bug in the Source Slack v2.1.0 state for Threads stream may be missing in some connections, which leads to reading the stream full refreshly even when incremental mode is used and because of this destination may contain record duplicates. The Source Slack v2.2.0 fixes missing state issue, so state is emitted properly.

Users that sync Threads stream in Full Refresh sync mode can simply upgrade their connection to v3.0.0 and ignore Migration Steps.

Users that sync Threads stream in Incremental sync mode should firstly check the following criteria and if at least one of them is related to your connection Migration Steps should be applied.

## Before applying this change users should check:

1. Connection State for Threads stream: if Connection State for Threads stream is empty, please follow Migration Steps. 
2. Record duplicates in destinations for Threads stream: if destination contains record duplicates for Threads stream, please follow Migration Steps.

## How to check Connection State for Threads stream

1. Go to connection using Source Slack
2. Select the **Settings** tab.
3. Under **Connection state** section you can find a connection state json object, look for `streamDescriptor` with `"name": "threads"` and check `streamState` for it. 

If state looks similar to the example below, you should follow the Migration Steps:
```
...
{
    "streamDescriptor": {
      "name": "threads"
    },
    "streamState": {
      "__ab_no_cursor_state_message": true
    }
},
...
```

## Migration Steps

To clear your data for the `Threads` stream, follow the steps below:

1. Select **Connections** in the main nav bar.
   1. Select the connection(s) affected by the update.
2. Select the **Status** tab.
   1. In the **Enabled streams** list, click the three dots on the right side of the `Threads` and select **Clear Data**.

After the clear succeeds, trigger a sync by clicking **Sync Now**. For more information on clearing your data in Airbyte, see [this page](/platform/operator-guides/clear).

## Upgrading to 2.0.0

As part of recent changes to the Slack API's [Terms of Service](https://api.slack.com/changelog/2025-05-terms-rate-limit-update-and-faq), we are migrating to a new Marketplace OAuth application. Users will need to re-authenticate their source with the new application to refresh their access token that is used to retrieve data. This does not apply if you use an API token, are on OSS, or supply your own Slack OAuth application credentials.

## Migration Steps

On the Airbyte application, navigate to your Slack source.

1. Under Authentication mechanism, click `Authenticate your Slack account`.
2. Follow the instructions in the pop-up window and click `Allow` to grant permissions to access your workspace.

## Upgrading to 1.0.0

We're continuously striving to enhance the quality and reliability of our connectors at Airbyte. As part of our commitment to delivering exceptional service, we are transitioning source Slack from the Python Connector Development Kit (CDK) to our innovative low-code framework. This is part of a strategic move to streamline many processes across connectors, bolstering maintainability and freeing us to focus more of our efforts on improving the performance and features of our evolving platform and growing catalog. However, due to differences between the Python and low-code CDKs, this migration constitutes a breaking change.

We’ve evolved and standardized how state is managed for incremental streams that are nested within a parent stream. This change impacts how individual states are tracked and stored for each partition, using a more structured approach to ensure the most granular and flexible state management. This change will affect the `Channel Messages` stream.

## Migration Steps

Clearing your data is required in order to continue syncing `Channel Messages` successfully. To clear your data for the `Channel Messages` stream, follow the steps below:

1. Select **Connections** in the main nav bar.
   1. Select the connection(s) affected by the update.
2. Select the **Status** tab.
   1. In the **Enabled streams** list, click the three dots on the right side of the `Channel Messages` and select **Clear Data**.

After the clear succeeds, trigger a sync by clicking **Sync Now**. For more information on clearing your data in Airbyte, see [this page](/platform/operator-guides/clear).

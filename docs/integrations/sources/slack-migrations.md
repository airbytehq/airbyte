# Slack Migration Guide

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

# Manage Airbyte Cloud notifications

This page provides guidance on how to manage notifications for Airbyte Cloud, allowing you to stay up-to-date on the activities in your workspace. 

## Set up Slack notifications

To set up Slack notifications:

1. On the [Airbyte Cloud](http://cloud.airbyte.io) dashboard, click **Settings**.

2. Click **Notifications**.

3. [Create an Incoming Webhook for Slack](https://api.slack.com/messaging/webhooks).

4. Navigate back to the Airbyte Cloud dashboard > Settings > Notifications and enter the Webhook URL.

5. Toggle the **When sync fails** and **When sync succeeds** buttons as required.

6. Click **Save changes**.

## Enable schema update notifications

To get notified when your source schema changes: 
1. Make sure you have [Webhook notifications](https://docs.airbyte.com/cloud/managing-airbyte-cloud/manage-airbyte-cloud-notifications#set-up-slack-notifications) set up.

2. On the [Airbyte Cloud](http://cloud.airbyte.com/) dashboard, click **Connections** and select the connection you want to receive notifications for.

3. Click the **Settings** tab on the Connection page.

4. Toggle **Schema update notifications**.

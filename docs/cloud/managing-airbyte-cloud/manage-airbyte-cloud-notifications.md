# Manage notifications

This page provides guidance on how to manage notifications for Airbyte Cloud, allowing you to stay up-to-date on the activities in your workspace. 

## Notification Event Types

| Type of Notification   | Description                                                                                                         |
|------------------------|---------------------------------------------------------------------------------------------------------------------|
| Failed Syncs                          | A sync from any of your connections fails. Note that if sync runs frequently or if there are many syncs in the workspace these types of events can be noisy            |
| Successful Syncs                      | A sync from any of your connections succeeds. Note that if sync runs frequently or if there are many syncs in the workspace these types of events can be noisy
| Automated Connection Updates          | A connection is updated automatically (ex. a source schema is automatically updated)              |
| Connection Updates Requiring Action   | A connection update requires you to take action (ex. a breaking schema change is detected)                |
| Warning - Repeated Failures                 | A connection will be disabled soon due to repeated failures. It has failed 50 times consecutively or there were only failed jobs in the past 7 days               |
| Sync Disabled - Repeated Failures                         | A connection was automatically disabled due to repeated failures. It will be disabled when it has failed 100 times consecutively or has been failing for 14 days in a row               |
| Warning - Upgrade Required (email only)                         |       A new connector version is available and requires manual upgrade       |
| Sync Disabled - Upgrade Required (email only)                         |   One or more connections were automatically disabled due to a connector upgrade deadline passing
|

## Configure Notification Settings

To set up email notifications:

1. On the [Airbyte Cloud](http://cloud.airbyte.com) dashboard, click **Settings**.

2. Click **Notifications**.

3. Toggle which messages you'd like to receive from Airbyte. All email notifications will be sent by default to the creator of the workspace. To change the recipient, edit and save the **notification email recipient**. If you would like to send email notifications to more than one recipient, you can enter an email distribution list (ie Google Group) as the recipient.

4. Click **Save changes**.

To set up webhook notifications:

1. On the [Airbyte Cloud](http://cloud.airbyte.com) dashboard, click **Settings**.

2. Click **Notifications**.

3. Have a webhook URL ready if you plan to use webhook notifications. Using a Slack webook is recommended. [Create an Incoming Webhook for Slack](https://api.slack.com/messaging/webhooks).

4. Toggle the type of events you are interested to receive notifications for. 
	1. To enable webhook notifications, the webhook URL is required. For your convenience, we provide a 'test' function to send a test message to your webhook URL so you can make sure it's working as expected.

5. Click **Save changes**.

## Enable schema update notifications

To get notified when your source schema changes: 
1. Make sure you have `Automatic Connection Updates` and `Connection Updates Requiring Action` turned on for your desired notification channels; If these are off, even if you turned on schema update notifications in a connection's settings, Airbyte will *NOT* send out any notifications related to these types of events.

2. On the [Airbyte Cloud](http://cloud.airbyte.com/) dashboard, click **Connections** and select the connection you want to receive notifications for.

3. Click the **Settings** tab on the Connection page.

4. Toggle **Schema update notifications**.

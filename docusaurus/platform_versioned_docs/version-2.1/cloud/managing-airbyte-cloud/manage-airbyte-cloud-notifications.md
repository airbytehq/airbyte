---
products: all
---

# Manage notifications

If you want Airbyte to notify you about important events, use its built-in notification system.

## How it works

You configure notifications for each workspace separately. Once you do, Airbyte can send notifications to an email address, webhook, or both.

- Airbyte Cloud can send notifications to an email or webhook.

- Self-Managed versions of Airbyte can send notifications to a webhook, but not an email.

### Events Airbyte can notify you about

| Event                                   | Cloud    | Self-Managed | Description                                                                                                                                            |
| --------------------------------------- | -------- | ------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------ |
| **Failed syncs**                        | &#10003; | &#10003;     | A sync from any of your connections fails. If syncs runs frequently or if there are many syncs in the workspace, this event can be noisy.              |
| **Successful syncs**                    | &#10003; | &#10003;     | A sync from any of your connections succeeds. If syncs runs frequently or if there are many syncs in the workspace, this event can be noisy.           |
| **Connection Updates**                  | &#10003; | &#10003;     | A connection is updated automatically. For example, a source schema is automatically updated.                                                          |
| **Connection Updates Requiring Action** | &#10003; | &#10003;     | A connection update requires you to take action. For example, a breaking change.                                                                       |
| **Warning - Repeated Failures**         | &#10003; | &#10003;     | Airbyte is at risk of turning off a connection due to repeated failures. It has failed 20 times consecutively and his not been successful in the last 4 days. |
| **Sync Disabled - Repeated Failures**   | &#10003; | &#10003;     | Airbyte has turned off a connection due to repeated failures. It has failed 30 times consecutively and has not been successful in the last 7 days.     |
| **Warning - Upgrade Required**          | &#10003; |              | A new connector version is available, but you need to manually upgrade.                                                                                |
| **Sync Disabled - Upgrade Required**    | &#10003; |              | Airbyte turned off one or more connections automatically because you missed the deadline to upgrade the connector.                                     |

### Enabling schema update notifications

If you want Airbyte to notify you of source schema changes, enable the following notifications.

- `Connection Updates`
- `Connection Updates Requiring Action`.

If these are off, even if you turned on schema update notifications in a connection's settings, Airbyte won't send notifications about schema changes.

To edit this setting, click **Connections** and select the connection you want to receive notifications for. Click the **Settings** tab on the Connection page. In the **Advanced Settings**, toggle **Be notified when schema changes occur**.

## Set up email notifications (Cloud only)

Follow these steps to set up email notifications from Airbyte Cloud. Email notifications are not available from self-managed editions of Airbyte.

1. Click **Workspace settings** > **Notifications**.

2. Under **Email Notification Recipient**, enter the email you want to receive notifications. If you would like to send email notifications to more than one recipient, enter a distribution list as the recipient.

3. Use the toggles in the **Email** column to set which notifications you want to receive.

## Set up webhook notifications

Airbyte can send notifications to any generic webhook service. You can use the webhook to send a notification to Slack or trigger other downstream transformations.

### Example webhook payload

Open each section to see an example of the payload returned for the notification type.

:::info
Airbyte passes both the `data` payload along with text blocks that intended for Slack usage.
:::

<details>
  <summary>Failed sync</summary>

```json
{
    "data": {
        "workspace": {
            "id":"b510e39b-e9e2-4833-9a3a-963e51d35fb4",
            "name":"Workspace1",
            "url":"https://link/to/ws"
        },
        "connection":{
            "id":"64d901a1-2520-4d91-93c8-9df438668ff0",
            "name":"Connection",
            "url":"https://link/to/connection"
        },
        "source":{
            "id":"c0655b08-1511-4e72-b7da-24c5d54de532",
            "name":"Source",
            "url":"https://link/to/source"
        },
        "destination":{
            "id":"5621c38f-8048-4abb-85ca-b34ff8d9a298",
            "name":"Destination",
            "url":"https://link/to/destination"
        },
        "jobId":9988,
        "startedAt":"2024-01-01T00:00:00Z",
        "finishedAt":"2024-01-01T01:00:00Z",
        "bytesEmitted":1000,
        "bytesCommitted":90,
        "recordsEmitted":89,
        "recordsCommitted":45,
        "errorMessage":"Something failed",
        "errorType": "config_error",
        "errorOrigin": "source",
        "bytesEmittedFormatted": "1000 B",
        "bytesCommittedFormatted":"90 B",
        "success":false,
        "durationInSeconds":3600,
        "durationFormatted":"1 hours 0 min"
    }
}
```

`errorType` refers to the type of error that occurred, and may indicate the need for a followup action. For example `config_error` indicates a problem with the source or destination configuration. In this case, look to `errorOrigin`. `transient_error` indicates a temporary issue that may resolve itself.

</details>
<details>
  <summary>Successful sync</summary>

```json
{
    "data": {
        "workspace": {
            "id":"b510e39b-e9e2-4833-9a3a-963e51d35fb4",
            "name":"Workspace1",
            "url":"https://link/to/ws"
        },
        "connection":{
            "id":"64d901a1-2520-4d91-93c8-9df438668ff0",
            "name":"Connection",
            "url":"https://link/to/connection"
        },
        "source":{
            "id":"c0655b08-1511-4e72-b7da-24c5d54de532",
            "name":"Source",
            "url":"https://link/to/source"
        },
        "destination":{
            "id":"5621c38f-8048-4abb-85ca-b34ff8d9a298",
            "name":"Destination",
            "url":"https://link/to/destination"
        },
        "jobId":9988,
        "startedAt":"2024-01-01T00:00:00Z",
        "finishedAt":"2024-01-01T01:00:00Z",
        "bytesEmitted":1000,
        "bytesCommitted":1000,
        "recordsEmitted":89,
        "recordsCommitted":89,
        "bytesEmittedFormatted": "1000 B",
        "bytesCommittedFormatted":"90 B",
        "success":true,
        "durationInSeconds":3600,
        "durationFormatted":"1 hours 0 min"
    }
}
```

</details>

<details>
  <summary>Connection updates</summary>

Webhook doesn't contain payload and only works for Slack notifications.

</details>

<details>
  <summary>Connection updates requiring action</summary>

Webhook doesn't contain payload and only works for Slack notifications.

</details>

<details>
  <summary>Warning - Repeated Failures</summary>

Webhook doesn't contain payload and only works for Slack notifications.

</details>

<details>
  <summary>Sync Disabled - Repeated Failures</summary>

Webhook doesn't contain payload and only works for Slack notifications.

</details>
<details>
  <summary>Warning - Upgrade Required</summary>

Webhook doesn't contain payload and only works for Slack notifications.

</details>
<details>
  <summary>Sync Disabled - Upgrade Required</summary>

Webhook doesn't contain payload and only works for Slack notifications.

</details>

### Configure Slack notifications

The webhook notification integrates with Slack. To set up a Slack integration, you create a Slack app, then enable the webhook notification from Airbyte.

#### Part 1: Create a Slack app

1. Navigate to https://api.slack.com/apps/.

2. Click **Create an App**.

3. Click **From Scratch**. Enter an app name (for example, "Airbyte Notifications") and pick the Slack workspace you want it to operate in.

4. Click **Incoming Webhooks**.

5. Click the toggle in the top right to turn the feature on.

6. Click **Add New Webhook**.

7. Select the channel that you want to receive Airbyte notifications in.

8. Click **Allow** to give the app permissions to access the channel. Your webhook appears under "Webhook URLs for Your Workspace", and the bot for this app joins your selected channel.

9. Copy the webhook URL. It looks similar to `https://hooks.slack.com/services/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PM1`

#### Part 2: Enable the Slack notification from Airbyte

Once you have set up your Slack app, follow these steps to set up webhook notifications from Airbyte.

1. Click **Workspace settings** > **Notifications**.

2. Use the toggles in the **Webhook** column to set which notifications you want to receive.

3. Enter the webhook URL, which you copied earlier, for each webhook you enabled.

4. Click **Test** to send a message to the channel.

5. Click **Save changes**.

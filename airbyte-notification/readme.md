# airbyte-notification

Logic for handling notifications (e.g. success / failure) that are emitted from jobs.

## Key Files
* `NotificationClient.java` wraps the clients for the different notification providers that we integrate with. Additional clients for each integration are houses in this module (e.g. SlackNotificationClient).

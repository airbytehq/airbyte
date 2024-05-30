# OneSignal

This page contains the setup guide and reference information for the OneSignal source connector.

## Prerequisites

- [User Auth Key](https://documentation.onesignal.com/docs/accounts-and-keys#user-auth-key)
- Applications [credentials](https://documentation.onesignal.com/docs/accounts-and-keys) \(App Id & REST API Key\)

## Setup guide

### Step 1: Set up OneSignal

### Step 2: Set up the OneSignal connector in Airbyte

#### For Airbyte Cloud:

1. [Log into your Airbyte Cloud](https://cloud.airbyte.io/workspaces) account.
2. Click **Sources** and then click **+ New source**.
3. On the Set up the source page, select **OneSignal** from the **Source type** dropdown.
4. Enter a name for the OneSignal connector.
5. Enter [User Auth Key](https://documentation.onesignal.com/docs/accounts-and-keys#user-auth-key)
6. Enter Applications credentials (repeat for every application):
   1. Enter App Name (for internal purposes only)
   2. Enter [App ID](https://documentation.onesignal.com/docs/accounts-and-keys#app-id)
   3. Enter [REST API Key](https://documentation.onesignal.com/docs/accounts-and-keys#rest-api-key)
7. Enter the Start Date in format `YYYY-MM-DDTHH:mm:ssZ`
8. Enter Outcome names as comma separated values, e.g. `os__session_duration.count,os__click.count,` see the [API docs](https://documentation.onesignal.com/reference/view-outcomes) for more details.

#### For Airbyte Open Source:

1. Navigate to the Airbyte Open Source dashboard.
2. Click **Sources** and then click **+ New source**.
3. On the Set up the source page, select **OneSignal** from the Source type dropdown.
4. Enter the name for the OneSignal connector.
5. Enter [User Auth Key](https://documentation.onesignal.com/docs/accounts-and-keys#user-auth-key)
6. Enter Applications credentials (repeat for every application):
   1. Enter App Name (for internal purposes only)
   2. Enter [App ID](https://documentation.onesignal.com/docs/accounts-and-keys#app-id)
   3. Enter [REST API Key](https://documentation.onesignal.com/docs/accounts-and-keys#rest-api-key)
7. Enter the Start Date in format `YYYY-MM-DDTHH:mm:ssZ`
8. Enter Outcome names as comma separated values, e.g. `os__session_duration.count,os__click.count,` see the [API docs](https://documentation.onesignal.com/reference/view-outcomes) for more details.

## Supported sync modes

The OneSignal source connector supports the following [sync modes](https://docs.airbyte.com/cloud/core-concepts#connection-sync-modes):

- [Full Refresh - Overwrite](https://docs.airbyte.com/understanding-airbyte/connections/full-refresh-overwrite/)
- [Full Refresh - Append](https://docs.airbyte.com/understanding-airbyte/connections/full-refresh-append)
- [Incremental - Append](https://docs.airbyte.com/understanding-airbyte/connections/incremental-append)
- [Incremental - Append + Deduped](https://docs.airbyte.com/understanding-airbyte/connections/incremental-append-deduped)

## Supported Streams

- [Apps](https://documentation.onesignal.com/reference/view-apps-apps)
- [Devices](https://documentation.onesignal.com/reference/view-devices) \(Incremental\)
- [Notifications](https://documentation.onesignal.com/reference/view-notification) \(Incremental\)
- [Outcomes](https://documentation.onesignal.com/reference/view-outcomes)

## Performance considerations

The connector is restricted by normal OneSignal [rate limits](https://documentation.onesignal.com/docs/rate-limits).

## Data type mapping

| Integration Type | Airbyte Type | Notes |
| :--------------- | :----------- | :---- |
| `string`         | `string`     |       |
| `integer`        | `integer`    |       |
| `number`         | `number`     |       |
| `array`          | `array`      |       |
| `object`         | `object`     |       |

## Changelog

| Version | Date       | Pull Request                                             | Subject                                      |
| :------ | :--------- | :------------------------------------------------------- | :------------------------------------------- |
| 1.1.0   | 2023-08-31 | [28941](https://github.com/airbytehq/airbyte/pull/28941) | Migrate connector to low-code                |
| 1.0.1   | 2023-03-14 | [24076](https://github.com/airbytehq/airbyte/pull/24076) | Fix schema and add additionalProperties true |
| 1.0.0   | 2023-03-14 | [24076](https://github.com/airbytehq/airbyte/pull/24076) | Update connectors spec; fix incremental sync |
| 0.1.2   | 2021-12-07 | [8582](https://github.com/airbytehq/airbyte/pull/8582)   | Update connector fields title/description    |
| 0.1.1   | 2021-11-10 | [7617](https://github.com/airbytehq/airbyte/pull/7617)   | Fix get_update state                         |
| 0.1.0   | 2021-10-13 | [6998](https://github.com/airbytehq/airbyte/pull/6998)   | Initial Release                              |

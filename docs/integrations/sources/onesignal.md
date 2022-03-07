# OneSignal

## Sync overview

This source can sync data for the [OneSignal API](https://documentation.onesignal.com/reference). It supports both Full Refresh and Incremental syncs. You can choose if this connector will copy only the new or updated data, or all rows in the tables and columns you set up for replication, every time a sync is run.

### Output schema

This Source is capable of syncing the following core Streams:

* [Apps](https://documentation.onesignal.com/reference/view-apps-apps)
* [Devices](https://documentation.onesignal.com/reference/view-devices) \(Incremental\)
* [Notifications](https://documentation.onesignal.com/reference/view-notification) \(Incremental\)
* [Outcomes](https://documentation.onesignal.com/reference/view-outcomes)

The `Outcomes` stream requires `outcome_names` parameter to filter out outcomes, see the [API docs](https://documentation.onesignal.com/reference/view-outcomes) for more details.

### Data type mapping

| Integration Type | Airbyte Type | Notes |
| :--- | :--- | :--- |
| `string` | `string` |  |
| `integer` | `integer` |  |
| `number` | `number` |  |
| `array` | `array` |  |
| `object` | `object` |  |

### Features

| Feature | Supported?\(Yes/No\) | Notes |
| :--- | :--- | :--- |
| Full Refresh Sync | Yes |  |
| Incremental Sync | Yes |  |
| Namespaces | No |  |

### Performance considerations

The connector is restricted by normal OneSignal [rate limits](https://documentation.onesignal.com/docs/rate-limits).

The OneSignal connector should not run into OneSignal API limitations under normal usage. Please [create an issue](https://github.com/airbytehq/airbyte/issues) if you see any rate limit issues that are not automatically retried successfully.

## Getting started

### Requirements

* OneSignal account
* OneSignal user auth Key

### Setup guide

Please register on OneSignal and follow this [docs](https://documentation.onesignal.com/docs/accounts-and-keys#user-auth-key) to get your user auth key.

## Changelog

| Version | Date | Pull Request | Subject |
| :--- | :--- | :--- | :--- |
| 0.1.2 | 2021-12-07 | [8582](https://github.com/airbytehq/airbyte/pull/8582) | Update connector fields title/description |
| 0.1.1 | 2021-11-10 | [7617](https://github.com/airbytehq/airbyte/pull/7617) | Fix get_update state |
| 0.1.0 | 2021-10-13 | [6998](https://github.com/airbytehq/airbyte/pull/6998) | Initial Release |


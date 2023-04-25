# Appstore

## Sync overview

This source can sync data for the [Appstore API](https://developer.apple.com/documentation/appstoreconnectapi). It supports only Incremental syncs. The Appstore API is available for [many types of services](https://developer.apple.com/documentation/appstoreconnectapi). Currently, this API supports syncing Sales and Trends reports. If you'd like to sync data from other endpoints, please create an issue on Github.

This Source Connector is based on a [Singer Tap](https://github.com/miroapp/tap-appstore).

### Output schema

This Source is capable of syncing the following "Sales and Trends" Streams:

* [SALES](https://help.apple.com/app-store-connect/#/dev15f9508ca)
* [SUBSCRIPTION](https://help.apple.com/app-store-connect/#/itc5dcdf6693)
* [SUBSCRIPTION\_EVENT](https://help.apple.com/app-store-connect/#/itc0b9b9d5b2)
* [SUBSCRIBER](https://help.apple.com/app-store-connect/#/itcf20f3392e)

Note that depending on the credentials you enter, you may only be able to sync some of these reports. For example, if your app does not offer subscriptions, then it is not possible to sync subscription related reports.

### Data type mapping

| Integration Type | Airbyte Type | Notes |
| :--- | :--- | :--- |
| `string` | `string` |  |
| `int`, `float`, `number` | `number` |  |
| `date` | `date` |  |
| `datetime` | `datetime` |  |
| `array` | `array` |  |
| `object` | `object` |  |

### Features

| Feature | Supported?\(Yes/No\) | Notes |
| :--- | :--- | :--- |
| Full Refresh Sync | no |  |
| Incremental Sync | yes |  |
| Namespaces | No |  |

### Performance considerations

The connector is restricted by normal Appstore [requests limitation](https://developer.apple.com/documentation/appstoreconnectapi/identifying_rate_limits).

The Appstore connector should not run into Appstore API limitations under normal usage. Please [create an issue](https://github.com/airbytehq/airbyte/issues) if you see any rate limit issues that are not automatically retried successfully.

One issue that can happen is the API not having the data available for the period requested, either because you're trying to request data older than 365 days or the today's and yesterday's data was not yet made available to be requested.

## Getting started

### Requirements

* Key ID
* Private Key The contents of the private API key file, which is in the P8 format and should start with `-----BEGIN PRIVATE KEY-----` and end with `-----END PRIVATE KEY-----`.
* Issuer ID
* Vendor ID Go to "Sales and Trends", then choose "Reports" from the drop-down menu in the top left. On the next screen, there'll be a drop-down menu for "Vendor". Your name and ID will be shown there. Use the numeric Vendor ID.
* Start Date \(The date that will be used in the first sync. Apple only allows to go back 365 days from today.\) Example: `2020-11-16T00:00:00Z`

### Setup guide

Generate/Find all requirements using this [external article](https://leapfin.com/blog/apple-appstore-integration/).

## Changelog

| Version | Date       | Pull Request | Subject                                         |
|:--------|:-----------| :--- |:------------------------------------------------|
| 0.2.6   | 2021-12-23 | [8434](https://github.com/airbytehq/airbyte/pull/8434) | Update fields in source-connectors specifications |
| 0.2.5   | 2021-12-09 | [7757](https://github.com/airbytehq/airbyte/pull/7757) | Migrate to the CDK                              |
| 0.2.4   | 2021-07-06 | [4539](https://github.com/airbytehq/airbyte/pull/4539) | Add `AIRBYTE_ENTRYPOINT` for Kubernetes support |


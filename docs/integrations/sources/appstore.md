# Appstore

## Sync overview

This source can sync data for the [Appstore API](https://developer.apple.com/documentation/appstoreconnectapi). It supports only Incremental syncs. The Applestore API is available for [many types of services](https://developer.apple.com/documentation/appstoreconnectapi), however this integration focuses only on the 'Reporting' service, from where data is extracted from.

Under the 'Reporting' Service, Appstore API has four different categories of Endpoints available.

1. Sales and Trends =&gt; [API docs](https://developer.apple.com/documentation/appstoreconnectapi/download_sales_and_trends_reports); ["UI docs"](https://help.apple.com/app-store-connect/#/dev061699fdb) 
2. Finance Reports =&gt; [API docs](https://developer.apple.com/documentation/appstoreconnectapi/download_finance_reports); ["UI docs"](https://help.apple.com/app-store-connect/#/dev716cf3a0d) 
3. Get Power and Performance Metrics for an App =&gt; [API docs](https://developer.apple.com/documentation/appstoreconnectapi/get_power_and_performance_metrics_for_an_app); 
4. Get Power and Performance Metrics for a Build =&gt; [API docs](https://developer.apple.com/documentation/appstoreconnectapi/get_power_and_performance_metrics_for_a_build);

This Source Connector is based on a [Singer Tap](https://github.com/miroapp/tap-appstore).

### Output schema

This Source is capable of syncing the following "Sales and Trends" Streams:

* [SALES](https://help.apple.com/app-store-connect/#/dev15f9508ca)
* [SUBSCRIPTION](https://help.apple.com/app-store-connect/#/itc5dcdf6693)
* [SUBSCRIPTION\_EVENT](https://help.apple.com/app-store-connect/#/itc0b9b9d5b2)
* [SUBSCRIBER](https://help.apple.com/app-store-connect/#/itcf20f3392e)

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


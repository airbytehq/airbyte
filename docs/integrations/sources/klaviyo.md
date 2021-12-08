# Klaviyo

## Sync overview

This source can sync data for the [Klaviyo API](https://apidocs.klaviyo.com/reference/api-overview). It supports both Full Refresh and Incremental syncs. You can choose if this connector will copy only the new or updated data, or all rows in the tables and columns you set up for replication, every time a sync is run.

### Output schema

This Source is capable of syncing the following core Streams:

* [Campaigns](https://apidocs.klaviyo.com/reference/campaigns#get-campaigns)
* [Events](https://apidocs.klaviyo.com/reference/metrics#metrics-timeline)
* [GlobalExclusions](https://apidocs.klaviyo.com/reference/lists-segments#get-global-exclusions)
* [Lists](https://apidocs.klaviyo.com/reference/lists#get-lists-deprecated)

### Data type mapping

| Integration Type | Airbyte Type | Notes |
| :--- | :--- | :--- |
| `string` | `string` |  |
| `number` | `number` |  |
| `array` | `array` |  |
| `object` | `object` |  |

### Features

| Feature | Supported?\(Yes/No\) | Notes |
| :--- | :--- | :--- |
| Full Refresh Sync | Yes |  |
| Incremental Sync | Yes | Only Events |
| Namespaces | No |  |

### Performance considerations

The connector is restricted by normal Klaviyo [requests limitation](https://apidocs.klaviyo.com/reference/api-overview#rate-limits).

The Klaviyo connector should not run into Klaviyo API limitations under normal usage. Please [create an issue](https://github.com/airbytehq/airbyte/issues) if you see any rate limit issues that are not automatically retried successfully.

## Getting started

### Requirements

* Klaviyo Private API Key

### Setup guide

<!-- markdown-link-check-disable-next-line -->
Please follow these [steps](https://help.klaviyo.com/hc/en-us/articles/115005062267-How-to-Manage-Your-Account-s-API-Keys#your-private-api-keys3) to obtain Private API Key for your account.

## CHANGELOG

| Version | Date       | Pull Request | Subject |
| :------ | :--------  | :-----       | :------ |
| `0.1.2` | 2021-10-19 | [6952](https://github.com/airbytehq/airbyte/pull/6952) | Update schema validation in SAT |

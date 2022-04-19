# Chartmogul

## Sync overview

The Chartmogul source supports Full Refresh syncs only.

This source syncs data for the [Chartmogul API](https://dev.chartmogul.com/reference/).

### Notes

If `start_date` is set, it will only apply to `Activities` stream. `Customers`' endpoint does not provide a way to filter by creation or update dates.

### Output schema

This Source is capable of syncing the following streams:

* [Customers](https://dev.chartmogul.com/reference/list-customers)
* [Activities](https://dev.chartmogul.com/reference/list-activities)

### Features

| Feature | Supported?\(Yes/No\)
| :--- | :--- |
| Full Refresh Sync | Yes |
| Incremental - Append Sync | No |
| Namespaces | No |

### Performance considerations

The Chartmogul connector should not run into Chartmogul API limitations under normal usage. Please [create an issue](https://github.com/airbytehq/airbyte/issues) if you see any rate limit issues that are not automatically retried successfully.

## Getting started

### Requirements

* Chartmogul Account
* Chartmogul API Key

### Setup guide

Please read [How to find your API key](https://dev.chartmogul.com/docs/authentication).

## Changelog

| Version | Date | Pull Request | Subject |
| :--- | :--- | :--- | :--- |
| 0.1.0 | 2022-01-10 | [9381](https://github.com/airbytehq/airbyte/pull/9381) | New Source: Chartmogul |

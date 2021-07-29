# Google Search Console

## Overview

The Google Search Console source supports both Full Refresh and Incremental syncs. You can choose if this connector will copy only the new or updated data, or all rows in the tables and columns you set up for replication, every time a sync is run.

This source wraps the [Singer Google Search Console Tap](https://github.com/singer-io/tap-google-search-console).

### Output schema

This Source is capable of syncing the following Streams:

* [Sites](https://developers.google.com/webmaster-tools/search-console-api-original/v3/sites/get)
* [Sitemaps](https://developers.google.com/webmaster-tools/search-console-api-original/v3/sitemaps/list)
* [Performance report country](https://developers.google.com/webmaster-tools/search-console-api-original/v3/searchanalytics/query)
* [Performance report custom](https://developers.google.com/webmaster-tools/search-console-api-original/v3/searchanalytics/query)
* [Performance report date](https://developers.google.com/webmaster-tools/search-console-api-original/v3/searchanalytics/query)
* [Performance report device](https://developers.google.com/webmaster-tools/search-console-api-original/v3/searchanalytics/query)
* [Performance report page](https://developers.google.com/webmaster-tools/search-console-api-original/v3/searchanalytics/query)
* [Performance report query \(keyword\)](https://developers.google.com/webmaster-tools/search-console-api-original/v3/searchanalytics/query)

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
| Incremental Sync | Yes | except Sites and Sitemaps |
| SSL connection | Yes |  |
| Namespaces | No |  |

### Performance considerations

This connector attempts to back off gracefully when it hits Reports API's rate limits. To find more information about limits, see [Usage Limits](https://developers.google.com/webmaster-tools/search-console-api-original/v3/limits) documentation.

## Getting started

### Requirements

* Credentials to a Google Service Account with delegated Domain Wide Authority
* Email address of the workspace admin which created the Service Account

### Create a Service Account with delegated domain wide authority

Follow the Google Documentation for performing [Delegating domain-wide authority](https://developers.google.com/identity/protocols/oauth2/service-account#delegatingauthority) to create a Service account with delegated domain wide authority. This account must be created by an administrator of the Google Workspace. Please make sure to grant the following OAuth scopes to the service user:

1. `https://www.googleapis.com/auth/webmasters.readonly`

At the end of this process, you should have JSON credentials to this Google Service Account.

You should now be ready to use the Google Workspace Admin Reports API connector in Airbyte.

## CHANGELOG

| Version | Date | Pull Request | Subject |
| :------ | :--------  | :-----       | :------ |
| `0.1.3` | 2021-07-06 | [4539](https://github.com/airbytehq/airbyte/pull/4539) | Add `AIRBYTE_ENTRYPOINT` for Kubernetes support |
